"""Photo annotation mapper — entity ↔ DTO translation."""

from app.application.dto.photo_annotation import (
    PhotoAnnotationCreateDTO,
    PhotoAnnotationResponseDTO,
    PhotoWithAnnotationsDTO,
)
from app.infrastructure.persistence.models.aircraft_model import (
    AircraftModelPhoto,
    PhotoAnnotation,
)
from app.infrastructure.storage.file_storage_service import FileStorageService


class PhotoAnnotationMapper:
    @staticmethod
    def to_entity(
        inspection_id: int, photo_id: int, dto: PhotoAnnotationCreateDTO
    ) -> PhotoAnnotation:
        return PhotoAnnotation(inspection_id=inspection_id, photo_id=photo_id, **dto.model_dump())

    @staticmethod
    def to_response_dto(annotation: PhotoAnnotation) -> PhotoAnnotationResponseDTO:
        return PhotoAnnotationResponseDTO.model_validate(annotation)

    @staticmethod
    def to_photo_with_annotations_dto(
        *,
        inspection_id: int,
        model_id: int,
        photo: AircraftModelPhoto,
        annotations: list[PhotoAnnotation],
        storage: FileStorageService,
    ) -> PhotoWithAnnotationsDTO:
        return PhotoWithAnnotationsDTO(
            inspection_id=inspection_id,
            photo_id=photo.id,
            model_id=model_id,
            url=storage.build_public_url(photo.file_path),
            caption=photo.caption,
            original_name=photo.original_name,
            annotations=[PhotoAnnotationMapper.to_response_dto(a) for a in annotations],
        )
