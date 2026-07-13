from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

AnnotationType = Literal["point", "line"]


class PhotoAnnotationCreateDTO(BaseModel):
    annotation_type: AnnotationType = "point"
    x_percent: float = Field(ge=0, le=100)
    y_percent: float = Field(ge=0, le=100)
    x2_percent: float | None = Field(default=None, ge=0, le=100)
    y2_percent: float | None = Field(default=None, ge=0, le=100)
    stroke_color: str = Field(default="#000000", max_length=20)
    stroke_width: int = Field(default=2, ge=1, le=12)
    section_label: str | None = Field(default=None, max_length=120)
    title: str = Field(min_length=1, max_length=200)
    notes: str | None = None

    @model_validator(mode="after")
    def validate_geometry(self) -> "PhotoAnnotationCreateDTO":
        if self.annotation_type == "line":
            if self.x2_percent is None or self.y2_percent is None:
                raise ValueError("Las líneas requieren punto final (x2_percent, y2_percent)")
        elif self.x2_percent is not None or self.y2_percent is not None:
            self.x2_percent = None
            self.y2_percent = None
        return self


class PhotoAnnotationUpdateDTO(BaseModel):
    annotation_type: AnnotationType | None = None
    x_percent: float | None = Field(default=None, ge=0, le=100)
    y_percent: float | None = Field(default=None, ge=0, le=100)
    x2_percent: float | None = Field(default=None, ge=0, le=100)
    y2_percent: float | None = Field(default=None, ge=0, le=100)
    stroke_color: str | None = Field(default=None, max_length=20)
    stroke_width: int | None = Field(default=None, ge=1, le=12)
    section_label: str | None = Field(default=None, max_length=120)
    title: str | None = Field(default=None, min_length=1, max_length=200)
    notes: str | None = None


class PhotoAnnotationResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    photo_id: int
    annotation_type: str
    x_percent: float
    y_percent: float
    x2_percent: float | None
    y2_percent: float | None
    stroke_color: str
    stroke_width: int
    section_label: str | None
    title: str
    notes: str | None
    created_at: datetime
    updated_at: datetime


class InspectionPhotoSummaryDTO(BaseModel):
    id: int
    url: str
    caption: str | None
    original_name: str | None
    is_primary: bool
    annotation_count: int = 0


class PhotoWithAnnotationsDTO(BaseModel):
    inspection_id: int
    photo_id: int
    model_id: int
    url: str
    caption: str | None
    original_name: str | None
    annotations: list[PhotoAnnotationResponseDTO]
