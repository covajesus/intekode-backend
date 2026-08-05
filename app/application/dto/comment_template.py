"""Comment template request and response DTOs."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CommentTemplateBaseDTO(BaseModel):
    body: str = Field(min_length=1, max_length=5000)

    @field_validator("body")
    @classmethod
    def normalize_body(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("El comentario no puede estar vacío")
        return normalized


class CommentTemplateCreateDTO(CommentTemplateBaseDTO):
    pass


class CommentTemplateUpdateDTO(CommentTemplateBaseDTO):
    pass


class CommentTemplateResponseDTO(CommentTemplateBaseDTO):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
