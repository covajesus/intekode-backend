"""Comment template entity/DTO mapper."""

from app.application.dto.comment_template import (
    CommentTemplateCreateDTO,
    CommentTemplateResponseDTO,
)
from app.infrastructure.persistence.models.comment_template import CommentTemplate


class CommentTemplateMapper:
    @staticmethod
    def to_entity(
        organization_id: int,
        dto: CommentTemplateCreateDTO,
    ) -> CommentTemplate:
        return CommentTemplate(
            organization_id=organization_id,
            body=dto.body,
        )

    @staticmethod
    def to_response_dto(template: CommentTemplate) -> CommentTemplateResponseDTO:
        return CommentTemplateResponseDTO.model_validate(template)
