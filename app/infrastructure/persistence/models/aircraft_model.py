from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base
from app.resources.checklist_template import DEFAULT_COMPONENTS, DEFAULT_SECTIONS


class PhotoAnnotation(Base):
    __tablename__ = "photo_annotations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    inspection_id: Mapped[int] = mapped_column(
        ForeignKey("inspections.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    photo_id: Mapped[int] = mapped_column(
        ForeignKey("aircraft_model_photos.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    x_percent: Mapped[float] = mapped_column(Float, nullable=False)
    y_percent: Mapped[float] = mapped_column(Float, nullable=False)
    x2_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    y2_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    annotation_type: Mapped[str] = mapped_column(String(20), default="point", nullable=False)
    stroke_color: Mapped[str] = mapped_column(String(20), default="#000000", nullable=False)
    stroke_width: Mapped[int] = mapped_column(Integer, default=2, nullable=False)
    section_label: Mapped[str | None] = mapped_column(String(120))
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    photo: Mapped["AircraftModelPhoto"] = relationship(back_populates="annotations")


class AircraftModel(Base):
    __tablename__ = "aircraft_models"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    manufacturer: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    model_name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    series: Mapped[str | None] = mapped_column(String(120))
    description: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    applicable_components: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=lambda: list(DEFAULT_COMPONENTS),
    )
    applicable_sections: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=lambda: list(DEFAULT_SECTIONS),
    )
    glb_file_name: Mapped[str | None] = mapped_column(String(255))
    glb_file_path: Mapped[str | None] = mapped_column(String(500))
    glb_original_name: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    photos: Mapped[list["AircraftModelPhoto"]] = relationship(
        back_populates="aircraft_model",
        cascade="all, delete-orphan",
        order_by="AircraftModelPhoto.sort_order",
    )
    model3d_annotations: Mapped[list["Model3DAnnotation"]] = relationship(
        back_populates="aircraft_model",
        cascade="all, delete-orphan",
        order_by="Model3DAnnotation.id",
    )


class AircraftModelPhoto(Base):
    __tablename__ = "aircraft_model_photos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    aircraft_model_id: Mapped[int] = mapped_column(
        ForeignKey("aircraft_models.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    original_name: Mapped[str | None] = mapped_column(String(255))
    caption: Mapped[str | None] = mapped_column(String(255))
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    aircraft_model: Mapped["AircraftModel"] = relationship(back_populates="photos")
    annotations: Mapped[list["PhotoAnnotation"]] = relationship(
        back_populates="photo",
        cascade="all, delete-orphan",
        order_by="PhotoAnnotation.id",
    )


class Model3DAnnotation(Base):
    """Inspection finding pinned on the shared aircraft-model GLB mesh."""

    __tablename__ = "model3d_annotations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    inspection_id: Mapped[int] = mapped_column(
        ForeignKey("inspections.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    aircraft_model_id: Mapped[int] = mapped_column(
        ForeignKey("aircraft_models.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    x: Mapped[float] = mapped_column(Float, nullable=False)
    y: Mapped[float] = mapped_column(Float, nullable=False)
    z: Mapped[float] = mapped_column(Float, nullable=False)
    color: Mapped[str] = mapped_column(String(20), default="#E53935", nullable=False)
    section_label: Mapped[str | None] = mapped_column(String(120))
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    aircraft_model: Mapped["AircraftModel"] = relationship(back_populates="model3d_annotations")
