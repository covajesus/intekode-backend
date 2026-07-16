from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class Model3DAnnotationCreateDTO(BaseModel):
    x: float
    y: float
    z: float
    color: str = Field(default="#E53935", max_length=20)
    section_label: str | None = Field(default=None, max_length=120)
    title: str = Field(min_length=1, max_length=200)
    notes: str | None = None


class Model3DAnnotationUpdateDTO(BaseModel):
    x: float | None = None
    y: float | None = None
    z: float | None = None
    color: str | None = Field(default=None, max_length=20)
    section_label: str | None = Field(default=None, max_length=120)
    title: str | None = Field(default=None, min_length=1, max_length=200)
    notes: str | None = None


class Model3DAnnotationResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    inspection_id: int
    aircraft_model_id: int
    x: float
    y: float
    z: float
    color: str
    section_label: str | None
    title: str
    notes: str | None
    created_at: datetime
    updated_at: datetime


class Model3DWithAnnotationsDTO(BaseModel):
    inspection_id: int
    model_id: int
    glb_url: str | None
    glb_original_name: str | None
    annotation_count: int = 0
    annotations: list[Model3DAnnotationResponseDTO] = Field(default_factory=list)
