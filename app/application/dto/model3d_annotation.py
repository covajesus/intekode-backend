from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

AnnotationType3D = Literal["point", "line"]


class Model3DAnnotationCreateDTO(BaseModel):
    annotation_type: AnnotationType3D = "line"
    x: float
    y: float
    z: float
    x2: float | None = None
    y2: float | None = None
    z2: float | None = None
    color: str = Field(default="#E53935", max_length=20)
    section_label: str | None = Field(default=None, max_length=120)
    title: str = Field(min_length=1, max_length=200)
    notes: str | None = None

    @model_validator(mode="after")
    def validate_geometry(self) -> "Model3DAnnotationCreateDTO":
        if self.annotation_type == "line":
            if self.x2 is None or self.y2 is None or self.z2 is None:
                raise ValueError("Las líneas 3D requieren punto final (x2, y2, z2)")
        else:
            self.x2 = None
            self.y2 = None
            self.z2 = None
        return self


class Model3DAnnotationUpdateDTO(BaseModel):
    annotation_type: AnnotationType3D | None = None
    x: float | None = None
    y: float | None = None
    z: float | None = None
    x2: float | None = None
    y2: float | None = None
    z2: float | None = None
    color: str | None = Field(default=None, max_length=20)
    section_label: str | None = Field(default=None, max_length=120)
    title: str | None = Field(default=None, min_length=1, max_length=200)
    notes: str | None = None


class Model3DAnnotationResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    inspection_id: int
    aircraft_model_id: int
    annotation_type: str
    x: float
    y: float
    z: float
    x2: float | None
    y2: float | None
    z2: float | None
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
