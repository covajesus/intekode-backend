"""SQLAlchemy repository for reusable comment templates."""

from sqlalchemy.orm import Session

from app.domain.interfaces.repositories import ICommentTemplateRepository
from app.infrastructure.persistence.models.comment_template import CommentTemplate


class SqlAlchemyCommentTemplateRepository(ICommentTemplateRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_by_organization(self, organization_id: int) -> list[CommentTemplate]:
        return (
            self._session.query(CommentTemplate)
            .filter(CommentTemplate.organization_id == organization_id)
            .order_by(CommentTemplate.body, CommentTemplate.id)
            .all()
        )

    def get_by_id(
        self,
        organization_id: int,
        template_id: int,
    ) -> CommentTemplate | None:
        return (
            self._session.query(CommentTemplate)
            .filter(
                CommentTemplate.id == template_id,
                CommentTemplate.organization_id == organization_id,
            )
            .first()
        )

    def create(self, template: CommentTemplate) -> CommentTemplate:
        self._session.add(template)
        return template

    def delete(self, template: CommentTemplate) -> None:
        self._session.delete(template)

    def commit(self) -> None:
        self._session.commit()

    def refresh(self, entity: CommentTemplate) -> CommentTemplate:
        self._session.refresh(entity)
        return entity
