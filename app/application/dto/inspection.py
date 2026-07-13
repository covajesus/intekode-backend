from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class ComponentSerialDTO(BaseModel):
    component_type: str
    received_sn: str | None = None
    installed_sn: str | None = None


class ComponentSerialResponseDTO(ComponentSerialDTO):
    model_config = ConfigDict(from_attributes=True)
    id: int


class ChecklistItemDTO(BaseModel):
    chapter: str
    section: str
    item_key: str
    item_label: str
    status: str | None = None
    comments: str | None = None


class ChecklistItemResponseDTO(ChecklistItemDTO):
    model_config = ConfigDict(from_attributes=True)
    id: int


class DiscrepancyDTO(BaseModel):
    item_number: int
    chapter: str
    description: str
    status: str | None = None


class DiscrepancyResponseDTO(DiscrepancyDTO):
    model_config = ConfigDict(from_attributes=True)
    id: int


class InspectionBaseDTO(BaseModel):
    aircraft_model_id: int | None = None
    aircraft_model: str | None = None
    operator: str | None = None
    msn: str | None = None
    registration: str | None = None
    inspection_date: date | None = None
    revision: str | None = None
    configuration: str | None = None
    total_hours: float | None = None
    total_cycles: int | None = None
    location: str | None = None
    facilities: str | None = None
    performed_by: str | None = None
    fuel_on_board_kg: float | None = None
    measurement_system: str | None = None
    pictures_available: str | None = None
    overall_rating: str | None = None
    chapter_ratings: str | None = None
    summary_comments: str | None = None
    signed_by: str | None = None
    signed_date: date | None = None


class InspectionCreateDTO(InspectionBaseDTO):
    status: str = "draft"
    component_serials: list[ComponentSerialDTO] = Field(default_factory=list)
    checklist_items: list[ChecklistItemDTO] = Field(default_factory=list)
    discrepancies: list[DiscrepancyDTO] = Field(default_factory=list)


class InspectionUpdateDTO(InspectionBaseDTO):
    status: str | None = None
    component_serials: list[ComponentSerialDTO] | None = None
    checklist_items: list[ChecklistItemDTO] | None = None
    discrepancies: list[DiscrepancyDTO] | None = None


class InspectionSummaryDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    aircraft_model_id: int | None
    aircraft_model: str | None
    operator: str | None
    msn: str | None
    registration: str | None
    inspection_date: date | None
    overall_rating: str | None
    created_at: datetime
    updated_at: datetime


class InspectionResponseDTO(InspectionBaseDTO):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    created_by: int
    created_at: datetime
    updated_at: datetime
    component_serials: list[ComponentSerialResponseDTO] = Field(default_factory=list)
    checklist_items: list[ChecklistItemResponseDTO] = Field(default_factory=list)
    discrepancies: list[DiscrepancyResponseDTO] = Field(default_factory=list)


class InspectionTemplateDTO(BaseModel):
    checklist: list[dict]
    default_components: list[str]
    chapter_ratings: list[dict]
    overall_ratings: list[str]
    section_ratings: list[str]
