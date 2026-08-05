"""Create the tenant-scoped reusable comment_templates table."""

from sqlalchemy import inspect, text

from app.infrastructure.database.session import engine


def migrate() -> None:
    if inspect(engine).has_table("comment_templates"):
        print("La tabla comment_templates ya existe.")
        return

    with engine.begin() as conn:
        conn.execute(
            text(
                """
                CREATE TABLE comment_templates (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    organization_id INT NOT NULL,
                    body TEXT NOT NULL,
                    created_at DATETIME NULL,
                    updated_at DATETIME NULL,
                    INDEX ix_comment_templates_organization_id (organization_id),
                    CONSTRAINT fk_comment_templates_organization
                        FOREIGN KEY (organization_id)
                        REFERENCES organizations(id)
                        ON DELETE CASCADE
                )
                """
            )
        )

    print("Migración comment_templates aplicada correctamente.")


if __name__ == "__main__":
    migrate()
