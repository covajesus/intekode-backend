"""Add applicable_components and applicable_sections to aircraft_models."""

import json

from sqlalchemy import inspect, text

from app.infrastructure.database.session import engine
from app.resources.checklist_template import DEFAULT_COMPONENTS, DEFAULT_SECTIONS


def _column_exists(table: str, column: str) -> bool:
    return column in [c["name"] for c in inspect(engine).get_columns(table)]


def migrate() -> None:
    components_json = json.dumps(DEFAULT_COMPONENTS)
    sections_json = json.dumps(DEFAULT_SECTIONS)

    with engine.begin() as conn:
        if not _column_exists("aircraft_models", "applicable_components"):
            conn.execute(
                text(
                    "ALTER TABLE aircraft_models "
                    "ADD COLUMN applicable_components JSON NULL "
                    "AFTER is_active"
                )
            )
            conn.execute(
                text(
                    "UPDATE aircraft_models "
                    "SET applicable_components = CAST(:payload AS JSON) "
                    "WHERE applicable_components IS NULL"
                ),
                {"payload": components_json},
            )

        if not _column_exists("aircraft_models", "applicable_sections"):
            after_col = (
                "applicable_components"
                if _column_exists("aircraft_models", "applicable_components")
                else "is_active"
            )
            conn.execute(
                text(
                    f"ALTER TABLE aircraft_models "
                    f"ADD COLUMN applicable_sections JSON NULL "
                    f"AFTER {after_col}"
                )
            )
            conn.execute(
                text(
                    "UPDATE aircraft_models "
                    "SET applicable_sections = CAST(:payload AS JSON) "
                    "WHERE applicable_sections IS NULL"
                ),
                {"payload": sections_json},
            )

    print("Migración applicable_components/sections aplicada correctamente.")


if __name__ == "__main__":
    migrate()
