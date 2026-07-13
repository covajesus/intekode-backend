"""Photo annotation repository — SQLAlchemy implementation."""

from sqlalchemy.orm import Session

from app.domain.interfaces.repositories import IPhotoAnnotationRepository
from app.infrastructure.persistence.models.aircraft_model import PhotoAnnotation


class SqlAlchemyPhotoAnnotationRepository(IPhotoAnnotationRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_by_inspection_photo(self, inspection_id: int, photo_id: int) -> list[PhotoAnnotation]:
        return (
            self._session.query(PhotoAnnotation)
            .filter(
                PhotoAnnotation.inspection_id == inspection_id,
                PhotoAnnotation.photo_id == photo_id,
            )
            .order_by(PhotoAnnotation.id)
            .all()
        )

    def get_by_id(
        self, inspection_id: int, photo_id: int, annotation_id: int
    ) -> PhotoAnnotation | None:
        return (
            self._session.query(PhotoAnnotation)
            .filter(
                PhotoAnnotation.id == annotation_id,
                PhotoAnnotation.inspection_id == inspection_id,
                PhotoAnnotation.photo_id == photo_id,
            )
            .first()
        )

    def create(self, annotation: PhotoAnnotation) -> PhotoAnnotation:
        self._session.add(annotation)
        return annotation

    def delete(self, annotation: PhotoAnnotation) -> None:
        self._session.delete(annotation)

    def commit(self) -> None:
        self._session.commit()

    def refresh(self, entity: PhotoAnnotation) -> PhotoAnnotation:
        self._session.refresh(entity)
        return entity
