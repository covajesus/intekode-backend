"""Aircraft model repository."""

from sqlalchemy.orm import Session, joinedload

from app.domain.interfaces.repositories import IAircraftModelRepository
from app.infrastructure.persistence.models.aircraft_model import AircraftModel, AircraftModelPhoto


class SqlAlchemyAircraftModelRepository(IAircraftModelRepository):
    _EAGER_LOAD = joinedload(AircraftModel.photos)

    def __init__(self, session: Session) -> None:
        self._session = session

    def list_by_organization(self, organization_id: int) -> list[AircraftModel]:
        return (
            self._session.query(AircraftModel)
            .options(self._EAGER_LOAD)
            .filter(AircraftModel.organization_id == organization_id)
            .order_by(AircraftModel.manufacturer, AircraftModel.model_name)
            .all()
        )

    def get_by_id(self, organization_id: int, model_id: int) -> AircraftModel | None:
        return (
            self._session.query(AircraftModel)
            .options(self._EAGER_LOAD)
            .filter(
                AircraftModel.id == model_id,
                AircraftModel.organization_id == organization_id,
            )
            .first()
        )

    def create(self, model: AircraftModel) -> AircraftModel:
        self._session.add(model)
        return model

    def delete(self, model: AircraftModel) -> None:
        self._session.delete(model)

    def add_photo(self, photo: AircraftModelPhoto) -> AircraftModelPhoto:
        self._session.add(photo)
        return photo

    def get_photo(self, model_id: int, photo_id: int) -> AircraftModelPhoto | None:
        return (
            self._session.query(AircraftModelPhoto)
            .filter(
                AircraftModelPhoto.id == photo_id,
                AircraftModelPhoto.aircraft_model_id == model_id,
            )
            .first()
        )

    def delete_photo(self, photo: AircraftModelPhoto) -> None:
        self._session.delete(photo)

    def clear_primary_photos(self, model_id: int) -> None:
        (
            self._session.query(AircraftModelPhoto)
            .filter(AircraftModelPhoto.aircraft_model_id == model_id)
            .update({AircraftModelPhoto.is_primary: False})
        )

    def commit(self) -> None:
        self._session.commit()

    def refresh(self, entity: AircraftModel | AircraftModelPhoto):
        self._session.refresh(entity)
        return entity
