"""Inspection repository — SQLAlchemy implementation with eager loading."""

from sqlalchemy import delete, select
from sqlalchemy.orm import Session, joinedload

from app.domain.interfaces.repositories import IInspectionRepository
from app.infrastructure.persistence.models.aircraft_model import (
    Model3DAnnotation,
    Model3DAnnotationPhoto,
    PhotoAnnotation,
)
from app.infrastructure.persistence.models.inspection import Inspection


class SqlAlchemyInspectionRepository(IInspectionRepository):
    _EAGER_LOAD = (
        joinedload(Inspection.component_serials),
        joinedload(Inspection.checklist_items),
        joinedload(Inspection.discrepancies),
        joinedload(Inspection.photo_annotations),
        joinedload(Inspection.model3d_annotations).joinedload(Model3DAnnotation.photos),
    )

    def __init__(self, session: Session) -> None:
        self._session = session

    def list_by_organization(self, organization_id: int) -> list[Inspection]:
        return (
            self._session.query(Inspection)
            .filter(Inspection.organization_id == organization_id)
            .order_by(Inspection.updated_at.desc())
            .all()
        )

    def get_by_id(self, organization_id: int, inspection_id: int) -> Inspection | None:
        return (
            self._session.query(Inspection)
            .options(*self._EAGER_LOAD)
            .filter(
                Inspection.id == inspection_id,
                Inspection.organization_id == organization_id,
            )
            .first()
        )

    def get_by_public_share_token(self, token: str) -> Inspection | None:
        if not token:
            return None
        return (
            self._session.query(Inspection)
            .options(*self._EAGER_LOAD)
            .filter(Inspection.public_share_token == token)
            .first()
        )

    def create(self, inspection: Inspection) -> Inspection:
        self._session.add(inspection)
        return inspection

    def delete(self, inspection: Inspection) -> None:
        # Explicit child cleanup so delete works even when DB FKs lack ON DELETE CASCADE
        # and when ORM cascades conflict across shared parents (aircraft model vs inspection).
        annotation_ids = list(
            self._session.scalars(
                select(Model3DAnnotation.id).where(
                    Model3DAnnotation.inspection_id == inspection.id
                )
            )
        )
        if annotation_ids:
            self._session.execute(
                delete(Model3DAnnotationPhoto).where(
                    Model3DAnnotationPhoto.annotation_id.in_(annotation_ids)
                )
            )
            self._session.execute(
                delete(Model3DAnnotation).where(Model3DAnnotation.id.in_(annotation_ids))
            )

        self._session.execute(
            delete(PhotoAnnotation).where(PhotoAnnotation.inspection_id == inspection.id)
        )
        self._session.delete(inspection)

    def commit(self) -> None:
        self._session.commit()

    def refresh(self, entity: Inspection) -> Inspection:
        self._session.refresh(entity)
        return entity
