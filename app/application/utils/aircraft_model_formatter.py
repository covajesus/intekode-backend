"""Aircraft model formatting utilities for inspection reports."""

from app.infrastructure.persistence.models.aircraft_model import AircraftModel


def format_catalog_model_label(model: AircraftModel) -> str:
    parts = [model.manufacturer, model.model_name]
    if model.series:
        parts.append(f"— {model.series}")
    return " ".join(part for part in parts if part)


def format_inspection_model_name(model: AircraftModel) -> str:
    """Value stored in inspection.aircraft_model (e.g. A330-301)."""
    return model.series or model.model_name
