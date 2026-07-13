from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base


class Inspection(Base):
    __tablename__ = "inspections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    status: Mapped[str] = mapped_column(String(20), default="draft")
    aircraft_model_id: Mapped[int | None] = mapped_column(
        ForeignKey("aircraft_models.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    aircraft_model: Mapped[str | None] = mapped_column(String(50))
    operator: Mapped[str | None] = mapped_column(String(120))
    msn: Mapped[str | None] = mapped_column(String(20))
    registration: Mapped[str | None] = mapped_column(String(20))
    inspection_date: Mapped[date | None] = mapped_column(Date)
    revision: Mapped[str | None] = mapped_column(String(50))
    configuration: Mapped[str | None] = mapped_column(String(50))
    total_hours: Mapped[float | None] = mapped_column(Float)
    total_cycles: Mapped[int | None] = mapped_column(Integer)
    location: Mapped[str | None] = mapped_column(String(200))
    facilities: Mapped[str | None] = mapped_column(String(200))
    performed_by: Mapped[str | None] = mapped_column(String(200))
    fuel_on_board_kg: Mapped[float | None] = mapped_column(Float)
    measurement_system: Mapped[str | None] = mapped_column(String(20))
    pictures_available: Mapped[str | None] = mapped_column(String(10))
    overall_rating: Mapped[str | None] = mapped_column(String(50))
    chapter_ratings: Mapped[str | None] = mapped_column(Text)
    summary_comments: Mapped[str | None] = mapped_column(Text)
    signed_by: Mapped[str | None] = mapped_column(String(120))
    signed_date: Mapped[date | None] = mapped_column(Date)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    component_serials: Mapped[list["ComponentSerial"]] = relationship(
        back_populates="inspection", cascade="all, delete-orphan"
    )
    checklist_items: Mapped[list["ChecklistItem"]] = relationship(
        back_populates="inspection", cascade="all, delete-orphan"
    )
    discrepancies: Mapped[list["Discrepancy"]] = relationship(
        back_populates="inspection", cascade="all, delete-orphan"
    )


class ComponentSerial(Base):
    __tablename__ = "component_serials"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    inspection_id: Mapped[int] = mapped_column(ForeignKey("inspections.id"), nullable=False)
    component_type: Mapped[str] = mapped_column(String(50), nullable=False)
    received_sn: Mapped[str | None] = mapped_column(String(80))
    installed_sn: Mapped[str | None] = mapped_column(String(80))

    inspection: Mapped["Inspection"] = relationship(back_populates="component_serials")


class ChecklistItem(Base):
    __tablename__ = "checklist_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    inspection_id: Mapped[int] = mapped_column(ForeignKey("inspections.id"), nullable=False)
    chapter: Mapped[str] = mapped_column(String(10), nullable=False)
    section: Mapped[str] = mapped_column(String(50), nullable=False)
    item_key: Mapped[str] = mapped_column(String(80), nullable=False)
    item_label: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str | None] = mapped_column(String(10))
    comments: Mapped[str | None] = mapped_column(Text)

    inspection: Mapped["Inspection"] = relationship(back_populates="checklist_items")


class Discrepancy(Base):
    __tablename__ = "discrepancies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    inspection_id: Mapped[int] = mapped_column(ForeignKey("inspections.id"), nullable=False)
    item_number: Mapped[int] = mapped_column(Integer, nullable=False)
    chapter: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str | None] = mapped_column(String(50))

    inspection: Mapped["Inspection"] = relationship(back_populates="discrepancies")
