"""Photo annotation application service — marks sections during inspections."""

from app.application.dto.photo_annotation import (
    InspectionPhotoSummaryDTO,
    PhotoAnnotationCreateDTO,
    PhotoAnnotationResponseDTO,
    PhotoAnnotationUpdateDTO,
    PhotoWithAnnotationsDTO,
)
from app.application.mappers.photo_annotation_mapper import PhotoAnnotationMapper
from app.core.exceptions import ApplicationError, NotFoundError
from app.domain.interfaces.repositories import (
    IAircraftModelRepository,
    IInspectionRepository,
    IPhotoAnnotationRepository,
)
from app.infrastructure.persistence.models.aircraft_model import PhotoAnnotation
from app.infrastructure.storage.file_storage_service import FileStorageService, file_storage_service


class PhotoAnnotationService:
    def __init__(
        self,
        inspection_repository: IInspectionRepository,
        aircraft_model_repository: IAircraftModelRepository,
        annotation_repository: IPhotoAnnotationRepository,
        storage: FileStorageService | None = None,
    ) -> None:
        self._inspections = inspection_repository
        self._aircraft_models = aircraft_model_repository
        self._annotations = annotation_repository
        self._storage = storage or file_storage_service

    def list_inspection_photos(
        self,
        organization_id: int,
        inspection_id: int,
    ) -> list[InspectionPhotoSummaryDTO]:
        inspection = self._get_inspection_or_raise(organization_id, inspection_id)
        if not inspection.aircraft_model_id:
            return []

        model = self._aircraft_models.get_by_id(organization_id, inspection.aircraft_model_id)
        if not model:
            return []

        summaries: list[InspectionPhotoSummaryDTO] = []
        for photo in model.photos:
            annotation_count = len(
                self._annotations.list_by_inspection_photo(inspection_id, photo.id)
            )
            summaries.append(
                InspectionPhotoSummaryDTO(
                    id=photo.id,
                    url=self._storage.build_public_url(photo.file_path),
                    caption=photo.caption,
                    original_name=photo.original_name,
                    is_primary=photo.is_primary,
                    annotation_count=annotation_count,
                )
            )
        return summaries

    def get_photo_with_annotations(
        self,
        organization_id: int,
        inspection_id: int,
        photo_id: int,
    ) -> PhotoWithAnnotationsDTO:
        inspection, photo = self._resolve_inspection_photo(
            organization_id, inspection_id, photo_id
        )
        annotations = self._annotations.list_by_inspection_photo(inspection_id, photo_id)
        return PhotoAnnotationMapper.to_photo_with_annotations_dto(
            inspection_id=inspection_id,
            model_id=inspection.aircraft_model_id,
            photo=photo,
            annotations=annotations,
            storage=self._storage,
        )

    def create_annotation(
        self,
        organization_id: int,
        inspection_id: int,
        photo_id: int,
        payload: PhotoAnnotationCreateDTO,
    ) -> PhotoAnnotationResponseDTO:
        self._resolve_inspection_photo(organization_id, inspection_id, photo_id)
        annotation = PhotoAnnotationMapper.to_entity(inspection_id, photo_id, payload)
        self._annotations.create(annotation)
        self._annotations.commit()
        self._annotations.refresh(annotation)
        return PhotoAnnotationMapper.to_response_dto(annotation)

    def update_annotation(
        self,
        organization_id: int,
        inspection_id: int,
        photo_id: int,
        annotation_id: int,
        payload: PhotoAnnotationUpdateDTO,
    ) -> PhotoAnnotationResponseDTO:
        self._resolve_inspection_photo(organization_id, inspection_id, photo_id)
        annotation = self._get_annotation_or_raise(inspection_id, photo_id, annotation_id)
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(annotation, key, value)
        self._annotations.commit()
        self._annotations.refresh(annotation)
        return PhotoAnnotationMapper.to_response_dto(annotation)

    def delete_annotation(
        self,
        organization_id: int,
        inspection_id: int,
        photo_id: int,
        annotation_id: int,
    ) -> None:
        self._resolve_inspection_photo(organization_id, inspection_id, photo_id)
        annotation = self._get_annotation_or_raise(inspection_id, photo_id, annotation_id)
        self._annotations.delete(annotation)
        self._annotations.commit()

    def _get_inspection_or_raise(self, organization_id: int, inspection_id: int):
        inspection = self._inspections.get_by_id(organization_id, inspection_id)
        if not inspection:
            raise NotFoundError("Inspección", inspection_id)
        return inspection

    def _resolve_inspection_photo(self, organization_id: int, inspection_id: int, photo_id: int):
        inspection = self._get_inspection_or_raise(organization_id, inspection_id)
        if not inspection.aircraft_model_id:
            raise ApplicationError(
                "La inspección no tiene un modelo de avión del catálogo vinculado",
                code="VALIDATION_ERROR",
            )

        photo = self._aircraft_models.get_photo(inspection.aircraft_model_id, photo_id)
        if not photo:
            raise NotFoundError("Foto", photo_id)
        return inspection, photo

    def _get_annotation_or_raise(
        self, inspection_id: int, photo_id: int, annotation_id: int
    ) -> PhotoAnnotation:
        annotation = self._annotations.get_by_id(inspection_id, photo_id, annotation_id)
        if not annotation:
            raise NotFoundError("Anotación", annotation_id)
        return annotation
