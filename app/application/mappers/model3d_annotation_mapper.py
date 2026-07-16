from app.application.dto.model3d_annotation import (
    Model3DAnnotationCreateDTO,
    Model3DAnnotationPhotoResponseDTO,
    Model3DAnnotationResponseDTO,
    Model3DWithAnnotationsDTO,
)
from app.infrastructure.persistence.models.aircraft_model import (
    AircraftModel,
    Model3DAnnotation,
)
from app.infrastructure.storage.file_storage_service import FileStorageService


class Model3DAnnotationMapper:
    @staticmethod
    def to_entity(
        inspection_id: int,
        aircraft_model_id: int,
        dto: Model3DAnnotationCreateDTO,
    ) -> Model3DAnnotation:
        return Model3DAnnotation(
            inspection_id=inspection_id,
            aircraft_model_id=aircraft_model_id,
            **dto.model_dump(),
        )

    @staticmethod
    def to_photo_dto(photo, storage: FileStorageService) -> Model3DAnnotationPhotoResponseDTO:
        return Model3DAnnotationPhotoResponseDTO(
            id=photo.id,
            annotation_id=photo.annotation_id,
            file_name=photo.file_name,
            file_path=photo.file_path,
            original_name=photo.original_name,
            sort_order=photo.sort_order,
            created_at=photo.created_at,
            url=storage.build_public_url(photo.file_path),
        )

    @staticmethod
    def to_response_dto(
        annotation: Model3DAnnotation,
        storage: FileStorageService | None = None,
    ) -> Model3DAnnotationResponseDTO:
        photos = []
        if storage is not None:
            photos = [
                Model3DAnnotationMapper.to_photo_dto(photo, storage)
                for photo in (annotation.photos or [])
            ]
        data = Model3DAnnotationResponseDTO.model_validate(annotation)
        return data.model_copy(update={"photos": photos})

    @staticmethod
    def to_model_with_annotations_dto(
        *,
        inspection_id: int,
        model: AircraftModel,
        annotations: list[Model3DAnnotation],
        storage: FileStorageService,
    ) -> Model3DWithAnnotationsDTO:
        glb_url = (
            storage.build_public_url(model.glb_file_path) if model.glb_file_path else None
        )
        return Model3DWithAnnotationsDTO(
            inspection_id=inspection_id,
            model_id=model.id,
            glb_url=glb_url,
            glb_original_name=model.glb_original_name,
            annotation_count=len(annotations),
            annotations=[
                Model3DAnnotationMapper.to_response_dto(a, storage) for a in annotations
            ],
        )
