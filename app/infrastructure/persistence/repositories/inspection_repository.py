"""Inspection repository — SQLAlchemy implementation with eager loading."""

from sqlalchemy.orm import Session, joinedload

from app.domain.interfaces.repositories import IInspectionRepository
from app.infrastructure.persistence.models.inspection import Inspection


class SqlAlchemyInspectionRepository(IInspectionRepository):
    _EAGER_LOAD = (
        joinedload(Inspection.component_serials),
        joinedload(Inspection.checklist_items),
        joinedload(Inspection.discrepancies),
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

    def create(self, inspection: Inspection) -> Inspection:
        self._session.add(inspection)
        return inspection

    def delete(self, inspection: Inspection) -> None:
        self._session.delete(inspection)

    def commit(self) -> None:
        self._session.commit()

    def refresh(self, entity: Inspection) -> Inspection:
        self._session.refresh(entity)
        return entity
