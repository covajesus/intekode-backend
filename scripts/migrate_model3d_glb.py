"""Add GLB columns to aircraft_models and create model3d_annotations table."""

from sqlalchemy import inspect, text

from app.infrastructure.database.session import engine


def _column_exists(table: str, column: str) -> bool:
    return column in [c["name"] for c in inspect(engine).get_columns(table)]


def _table_exists(table: str) -> bool:
    return table in inspect(engine).get_table_names()


def migrate() -> None:
    with engine.begin() as conn:
        if not _column_exists("aircraft_models", "glb_file_name"):
            conn.execute(text("ALTER TABLE aircraft_models ADD COLUMN glb_file_name VARCHAR(255) NULL"))
        if not _column_exists("aircraft_models", "glb_file_path"):
            conn.execute(text("ALTER TABLE aircraft_models ADD COLUMN glb_file_path VARCHAR(500) NULL"))
        if not _column_exists("aircraft_models", "glb_original_name"):
            conn.execute(
                text("ALTER TABLE aircraft_models ADD COLUMN glb_original_name VARCHAR(255) NULL")
            )

        if not _table_exists("model3d_annotations"):
            conn.execute(
                text(
                    """
                    CREATE TABLE model3d_annotations (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        inspection_id INT NOT NULL,
                        aircraft_model_id INT NOT NULL,
                        x DOUBLE NOT NULL,
                        y DOUBLE NOT NULL,
                        z DOUBLE NOT NULL,
                        x2 DOUBLE NULL,
                        y2 DOUBLE NULL,
                        z2 DOUBLE NULL,
                        annotation_type VARCHAR(20) NOT NULL DEFAULT 'line',
                        color VARCHAR(20) NOT NULL DEFAULT '#E53935',
                        section_label VARCHAR(120) NULL,
                        title VARCHAR(200) NOT NULL,
                        notes TEXT NULL,
                        created_at DATETIME NULL,
                        updated_at DATETIME NULL,
                        INDEX ix_model3d_annotations_inspection_id (inspection_id),
                        INDEX ix_model3d_annotations_aircraft_model_id (aircraft_model_id),
                        CONSTRAINT fk_model3d_annotations_inspection
                            FOREIGN KEY (inspection_id) REFERENCES inspections(id) ON DELETE CASCADE,
                        CONSTRAINT fk_model3d_annotations_model
                            FOREIGN KEY (aircraft_model_id) REFERENCES aircraft_models(id) ON DELETE CASCADE
                    )
                    """
                )
            )
        else:
            if not _column_exists("model3d_annotations", "x2"):
                conn.execute(text("ALTER TABLE model3d_annotations ADD COLUMN x2 DOUBLE NULL"))
            if not _column_exists("model3d_annotations", "y2"):
                conn.execute(text("ALTER TABLE model3d_annotations ADD COLUMN y2 DOUBLE NULL"))
            if not _column_exists("model3d_annotations", "z2"):
                conn.execute(text("ALTER TABLE model3d_annotations ADD COLUMN z2 DOUBLE NULL"))
            if not _column_exists("model3d_annotations", "annotation_type"):
                conn.execute(
                    text(
                        "ALTER TABLE model3d_annotations "
                        "ADD COLUMN annotation_type VARCHAR(20) NOT NULL DEFAULT 'line'"
                    )
                )

    print("Migración GLB / model3d_annotations aplicada correctamente.")


if __name__ == "__main__":
    migrate()
