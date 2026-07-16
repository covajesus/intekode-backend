from app.application.dto.model3d_annotation import (
    Model3DAnnotationCreateDTO,
    Model3DAnnotationResponseDTO,
    Model3DWithAnnotationsDTO,
)
from app.infrastructure.persistence.models.aircraft_model import AircraftModel, Model3DAnnotation
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
    def to_response_dto(annotation: Model3DAnnotation) -> Model3DAnnotationResponseDTO:
        return Model3DAnnotationResponseDTO.model_validate(annotation)

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
            annotations=[Model3DAnnotationMapper.to_response_dto(a) for a in annotations],
        )
