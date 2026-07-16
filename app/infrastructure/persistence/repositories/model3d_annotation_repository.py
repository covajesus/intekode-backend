"""Repository for 3D annotations pinned on aircraft-model GLB meshes."""

from sqlalchemy.orm import Session, joinedload

from app.domain.interfaces.repositories import IModel3DAnnotationRepository
from app.infrastructure.persistence.models.aircraft_model import (
    Model3DAnnotation,
    Model3DAnnotationPhoto,
)


class SqlAlchemyModel3DAnnotationRepository(IModel3DAnnotationRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_by_inspection(self, inspection_id: int) -> list[Model3DAnnotation]:
        return (
            self._session.query(Model3DAnnotation)
            .options(joinedload(Model3DAnnotation.photos))
            .filter(Model3DAnnotation.inspection_id == inspection_id)
            .order_by(Model3DAnnotation.id)
            .all()
        )

    def get_by_id(self, inspection_id: int, annotation_id: int) -> Model3DAnnotation | None:
        return (
            self._session.query(Model3DAnnotation)
            .options(joinedload(Model3DAnnotation.photos))
            .filter(
                Model3DAnnotation.id == annotation_id,
                Model3DAnnotation.inspection_id == inspection_id,
            )
            .first()
        )

    def add_photo(self, photo: Model3DAnnotationPhoto) -> Model3DAnnotationPhoto:
        self._session.add(photo)
        return photo

    def get_photo(self, annotation_id: int, photo_id: int) -> Model3DAnnotationPhoto | None:
        return (
            self._session.query(Model3DAnnotationPhoto)
            .filter(
                Model3DAnnotationPhoto.id == photo_id,
                Model3DAnnotationPhoto.annotation_id == annotation_id,
            )
            .first()
        )

    def delete_photo(self, photo: Model3DAnnotationPhoto) -> None:
        self._session.delete(photo)

    def create(self, annotation: Model3DAnnotation) -> Model3DAnnotation:
        self._session.add(annotation)
        return annotation

    def delete(self, annotation: Model3DAnnotation) -> None:
        self._session.delete(annotation)

    def commit(self) -> None:
        self._session.commit()

    def refresh(self, entity: Model3DAnnotation) -> Model3DAnnotation:
        self._session.refresh(entity)
        return entity
