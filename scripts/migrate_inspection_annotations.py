"""Move photo annotations to inspections and add line styling fields."""

from sqlalchemy import inspect, text

from app.infrastructure.database.session import engine


def _column_exists(table: str, column: str) -> bool:
    return column in [c["name"] for c in inspect(engine).get_columns(table)]


def migrate() -> None:
    with engine.begin() as conn:
        if not _column_exists("photo_annotations", "inspection_id"):
            conn.execute(text("DELETE FROM photo_annotations"))
            conn.execute(
                text("ALTER TABLE photo_annotations ADD COLUMN inspection_id INT NULL AFTER id")
            )
            conn.execute(text("ALTER TABLE photo_annotations MODIFY inspection_id INT NOT NULL"))

        fk_names = [
            fk.get("name")
            for fk in inspect(engine).get_foreign_keys("photo_annotations")
            if fk.get("name")
        ]
        if "fk_photo_annotations_inspection" not in fk_names:
            conn.execute(
                text(
                    "ALTER TABLE photo_annotations "
                    "ADD CONSTRAINT fk_photo_annotations_inspection "
                    "FOREIGN KEY (inspection_id) REFERENCES inspections(id) ON DELETE CASCADE"
                )
            )

        if not _column_exists("photo_annotations", "annotation_type"):
            conn.execute(
                text(
                    "ALTER TABLE photo_annotations "
                    "ADD COLUMN annotation_type VARCHAR(20) NOT NULL DEFAULT 'point' AFTER photo_id"
                )
            )
        if not _column_exists("photo_annotations", "x2_percent"):
            conn.execute(
                text("ALTER TABLE photo_annotations ADD COLUMN x2_percent FLOAT NULL AFTER y_percent")
            )
        if not _column_exists("photo_annotations", "y2_percent"):
            conn.execute(
                text("ALTER TABLE photo_annotations ADD COLUMN y2_percent FLOAT NULL AFTER x2_percent")
            )
        if not _column_exists("photo_annotations", "stroke_color"):
            conn.execute(
                text(
                    "ALTER TABLE photo_annotations "
                    "ADD COLUMN stroke_color VARCHAR(20) NOT NULL DEFAULT '#ef4444' AFTER y2_percent"
                )
            )
        if not _column_exists("photo_annotations", "stroke_width"):
            conn.execute(
                text(
                    "ALTER TABLE photo_annotations "
                    "ADD COLUMN stroke_width INT NOT NULL DEFAULT 3 AFTER stroke_color"
                )
            )

    print("Migración de anotaciones por inspección aplicada correctamente.")


if __name__ == "__main__":
    migrate()
