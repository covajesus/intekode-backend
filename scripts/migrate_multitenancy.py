"""Apply multi-tenant schema changes to an existing database."""

from sqlalchemy import inspect, text

from app.infrastructure.database.session import engine


def _column_exists(table: str, column: str) -> bool:
    return column in [c["name"] for c in inspect(engine).get_columns(table)]


def _index_exists(table: str, index_name: str) -> bool:
    return index_name in [i["name"] for i in inspect(engine).get_indexes(table)]


def _fk_exists(table: str, fk_name: str) -> bool:
    return fk_name in [fk["name"] for fk in inspect(engine).get_foreign_keys(table) if fk.get("name")]


def migrate() -> None:
    with engine.begin() as conn:
        org_id = conn.execute(
            text("SELECT id FROM organizations WHERE slug = 'demo' LIMIT 1")
        ).scalar()
        if org_id is None:
            conn.execute(
                text(
                    "INSERT INTO organizations (name, slug, is_active) "
                    "VALUES ('Cliente Demo', 'demo', 1)"
                )
            )
            org_id = conn.execute(
                text("SELECT id FROM organizations WHERE slug = 'demo' LIMIT 1")
            ).scalar()

        conn.execute(
            text(
                """
                INSERT INTO organization_members (organization_id, user_id, role)
                SELECT :org_id, u.id, 'admin'
                FROM users u
                WHERE u.username = 'admin'
                  AND NOT EXISTS (
                    SELECT 1 FROM organization_members om
                    WHERE om.organization_id = :org_id AND om.user_id = u.id
                  )
                """
            ),
            {"org_id": org_id},
        )

        if not _column_exists("inspections", "organization_id"):
            conn.execute(
                text("ALTER TABLE inspections ADD COLUMN organization_id INT NULL AFTER id")
            )
        conn.execute(
            text("UPDATE inspections SET organization_id = :org_id WHERE organization_id IS NULL"),
            {"org_id": org_id},
        )
        conn.execute(text("ALTER TABLE inspections MODIFY organization_id INT NOT NULL"))
        if not _index_exists("inspections", "idx_inspections_org"):
            conn.execute(
                text("ALTER TABLE inspections ADD INDEX idx_inspections_org (organization_id)")
            )
        if not _fk_exists("inspections", "fk_inspections_org"):
            conn.execute(
                text(
                    "ALTER TABLE inspections ADD CONSTRAINT fk_inspections_org "
                    "FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE"
                )
            )

        if not _column_exists("aircraft_models", "organization_id"):
            conn.execute(
                text("ALTER TABLE aircraft_models ADD COLUMN organization_id INT NULL AFTER id")
            )
        conn.execute(
            text(
                "UPDATE aircraft_models SET organization_id = :org_id WHERE organization_id IS NULL"
            ),
            {"org_id": org_id},
        )
        conn.execute(text("ALTER TABLE aircraft_models MODIFY organization_id INT NOT NULL"))
        if not _index_exists("aircraft_models", "idx_aircraft_models_org"):
            conn.execute(
                text(
                    "ALTER TABLE aircraft_models ADD INDEX idx_aircraft_models_org (organization_id)"
                )
            )
        if not _fk_exists("aircraft_models", "fk_aircraft_models_org"):
            conn.execute(
                text(
                    "ALTER TABLE aircraft_models ADD CONSTRAINT fk_aircraft_models_org "
                    "FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE"
                )
            )

    print("Migración multicliente aplicada correctamente.")


if __name__ == "__main__":
    migrate()
