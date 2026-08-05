"""Add permanent public share token column to inspections."""

from sqlalchemy import inspect, text

from app.infrastructure.database.session import engine


def _column_exists(table: str, column: str) -> bool:
    return column in [c["name"] for c in inspect(engine).get_columns(table)]


def migrate() -> None:
    with engine.begin() as conn:
        if not _column_exists("inspections", "public_share_token"):
            conn.execute(
                text(
                    "ALTER TABLE inspections "
                    "ADD COLUMN public_share_token VARCHAR(64) NULL "
                    "AFTER signed_date"
                )
            )
            conn.execute(
                text(
                    "CREATE UNIQUE INDEX ix_inspections_public_share_token "
                    "ON inspections (public_share_token)"
                )
            )
            print("Columna public_share_token agregada.")
        else:
            print("La columna public_share_token ya existe.")


if __name__ == "__main__":
    migrate()
