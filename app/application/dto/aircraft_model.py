from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AircraftModelPhotoDTO(BaseModel):
    caption: str | None = None
    is_primary: bool = False
    sort_order: int = 0


class AircraftModelPhotoResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    aircraft_model_id: int
    file_name: str
    file_path: str
    original_name: str | None
    caption: str | None
    is_primary: bool
    sort_order: int
    created_at: datetime
    url: str | None = None


class AircraftModelBaseDTO(BaseModel):
    manufacturer: str = Field(min_length=1, max_length=120)
    model_name: str = Field(min_length=1, max_length=120)
    series: str | None = Field(default=None, max_length=120)
    description: str | None = None
    is_active: bool = True
    applicable_components: list[str] = Field(default_factory=list)
    applicable_sections: list[str] = Field(default_factory=list)


class AircraftModelCreateDTO(AircraftModelBaseDTO):
    pass


class AircraftModelUpdateDTO(BaseModel):
    manufacturer: str | None = Field(default=None, min_length=1, max_length=120)
    model_name: str | None = Field(default=None, min_length=1, max_length=120)
    series: str | None = Field(default=None, max_length=120)
    description: str | None = None
    is_active: bool | None = None
    applicable_components: list[str] | None = None
    applicable_sections: list[str] | None = None


class AircraftModelSummaryDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    manufacturer: str
    model_name: str
    series: str | None
    is_active: bool
    applicable_components: list[str] = Field(default_factory=list)
    applicable_sections: list[str] = Field(default_factory=list)
    photo_count: int = 0
    primary_photo_url: str | None = None
    has_glb: bool = False
    created_at: datetime
    updated_at: datetime


class AircraftModelResponseDTO(AircraftModelBaseDTO):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
    photos: list[AircraftModelPhotoResponseDTO] = Field(default_factory=list)
    glb_file_name: str | None = None
    glb_original_name: str | None = None
    glb_url: str | None = None
