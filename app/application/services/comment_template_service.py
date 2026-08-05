"""Application service for reusable inspection comment templates."""

from app.application.dto.comment_template import (
    CommentTemplateCreateDTO,
    CommentTemplateResponseDTO,
    CommentTemplateUpdateDTO,
)
from app.application.mappers.comment_template_mapper import CommentTemplateMapper
from app.core.exceptions import NotFoundError
from app.domain.interfaces.repositories import ICommentTemplateRepository
from app.infrastructure.persistence.models.comment_template import CommentTemplate


class CommentTemplateService:
    def __init__(self, repository: ICommentTemplateRepository) -> None:
        self._repository = repository

    def list_templates(self, organization_id: int) -> list[CommentTemplateResponseDTO]:
        templates = self._repository.list_by_organization(organization_id)
        return [CommentTemplateMapper.to_response_dto(item) for item in templates]

    def get_template(
        self,
        organization_id: int,
        template_id: int,
    ) -> CommentTemplateResponseDTO:
        return CommentTemplateMapper.to_response_dto(
            self._get_or_raise(organization_id, template_id)
        )

    def create_template(
        self,
        organization_id: int,
        payload: CommentTemplateCreateDTO,
    ) -> CommentTemplateResponseDTO:
        template = CommentTemplateMapper.to_entity(organization_id, payload)
        self._repository.create(template)
        self._repository.commit()
        self._repository.refresh(template)
        return CommentTemplateMapper.to_response_dto(template)

    def update_template(
        self,
        organization_id: int,
        template_id: int,
        payload: CommentTemplateUpdateDTO,
    ) -> CommentTemplateResponseDTO:
        template = self._get_or_raise(organization_id, template_id)
        template.body = payload.body
        self._repository.commit()
        self._repository.refresh(template)
        return CommentTemplateMapper.to_response_dto(template)

    def delete_template(self, organization_id: int, template_id: int) -> None:
        template = self._get_or_raise(organization_id, template_id)
        self._repository.delete(template)
        self._repository.commit()

    def _get_or_raise(
        self,
        organization_id: int,
        template_id: int,
    ) -> CommentTemplate:
        template = self._repository.get_by_id(organization_id, template_id)
        if not template:
            raise NotFoundError("Plantilla de comentario", template_id)
        return template
