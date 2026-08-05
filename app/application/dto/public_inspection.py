"""Public read-only DTOs for shared 3D inspection views."""

from pydantic import BaseModel, Field


class PublicModel3DFindingDTO(BaseModel):
    id: int
    number: int
    annotation_type: str
    x: float
    y: float
    z: float
    x2: float | None = None
    y2: float | None = None
    z2: float | None = None
    color: str
    section_label: str | None = None
    title: str
    notes: str | None = None


class PublicModel3DViewDTO(BaseModel):
    registration: str | None = None
    aircraft_model: str | None = None
    has_glb: bool = False
    glb_original_name: str | None = None
    finding_count: int = 0
    findings: list[PublicModel3DFindingDTO] = Field(default_factory=list)
