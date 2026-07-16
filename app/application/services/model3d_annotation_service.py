"""3D model annotation service — pin findings on the aircraft GLB during inspections."""

from app.application.dto.model3d_annotation import (
    Model3DAnnotationCreateDTO,
    Model3DAnnotationResponseDTO,
    Model3DAnnotationUpdateDTO,
    Model3DWithAnnotationsDTO,
)
from app.application.mappers.model3d_annotation_mapper import Model3DAnnotationMapper
from app.core.exceptions import ApplicationError, NotFoundError
from app.domain.interfaces.repositories import (
    IAircraftModelRepository,
    IInspectionRepository,
    IModel3DAnnotationRepository,
)
from app.infrastructure.persistence.models.aircraft_model import Model3DAnnotation
from app.infrastructure.storage.file_storage_service import FileStorageService, file_storage_service


class Model3DAnnotationService:
    def __init__(
        self,
        inspection_repository: IInspectionRepository,
        aircraft_model_repository: IAircraftModelRepository,
        annotation_repository: IModel3DAnnotationRepository,
        storage: FileStorageService | None = None,
    ) -> None:
        self._inspections = inspection_repository
        self._aircraft_models = aircraft_model_repository
        self._annotations = annotation_repository
        self._storage = storage or file_storage_service

    def get_model_with_annotations(
        self,
        organization_id: int,
        inspection_id: int,
    ) -> Model3DWithAnnotationsDTO:
        inspection, model = self._resolve_inspection_model(organization_id, inspection_id)
        annotations = self._annotations.list_by_inspection(inspection_id)
        return Model3DAnnotationMapper.to_model_with_annotations_dto(
            inspection_id=inspection.id,
            model=model,
            annotations=annotations,
            storage=self._storage,
        )

    def create_annotation(
        self,
        organization_id: int,
        inspection_id: int,
        payload: Model3DAnnotationCreateDTO,
    ) -> Model3DAnnotationResponseDTO:
        inspection, model = self._resolve_inspection_model(organization_id, inspection_id)
        if not model.glb_file_path:
            raise ApplicationError(
                "El modelo de avión no tiene un archivo GLB cargado",
                code="VALIDATION_ERROR",
            )
        annotation = Model3DAnnotationMapper.to_entity(inspection.id, model.id, payload)
        self._annotations.create(annotation)
        self._annotations.commit()
        self._annotations.refresh(annotation)
        return Model3DAnnotationMapper.to_response_dto(annotation)

    def update_annotation(
        self,
        organization_id: int,
        inspection_id: int,
        annotation_id: int,
        payload: Model3DAnnotationUpdateDTO,
    ) -> Model3DAnnotationResponseDTO:
        self._resolve_inspection_model(organization_id, inspection_id)
        annotation = self._get_annotation_or_raise(inspection_id, annotation_id)
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(annotation, key, value)
        self._annotations.commit()
        self._annotations.refresh(annotation)
        return Model3DAnnotationMapper.to_response_dto(annotation)

    def delete_annotation(
        self,
        organization_id: int,
        inspection_id: int,
        annotation_id: int,
    ) -> None:
        self._resolve_inspection_model(organization_id, inspection_id)
        annotation = self._get_annotation_or_raise(inspection_id, annotation_id)
        self._annotations.delete(annotation)
        self._annotations.commit()

    def get_glb_file_path(
        self,
        organization_id: int,
        inspection_id: int,
    ) -> tuple[str, str]:
        """Return (absolute_path, download_filename) for the inspection model GLB."""
        _, model = self._resolve_inspection_model(organization_id, inspection_id)
        if not model.glb_file_path:
            raise NotFoundError("Modelo 3D (GLB)", inspection_id)

        absolute = self._storage.resolve_absolute_path(model.glb_file_path)
        if not absolute.exists() or not absolute.is_file():
            raise NotFoundError("Archivo GLB", inspection_id)

        filename = model.glb_original_name or model.glb_file_name or "model.glb"
        return str(absolute), filename

    def _get_inspection_or_raise(self, organization_id: int, inspection_id: int):
        inspection = self._inspections.get_by_id(organization_id, inspection_id)
        if not inspection:
            raise NotFoundError("Inspección", inspection_id)
        return inspection

    def _resolve_inspection_model(self, organization_id: int, inspection_id: int):
        inspection = self._get_inspection_or_raise(organization_id, inspection_id)
        if not inspection.aircraft_model_id:
            raise ApplicationError(
                "La inspección no tiene un modelo de avión del catálogo vinculado",
                code="VALIDATION_ERROR",
            )

        model = self._aircraft_models.get_by_id(organization_id, inspection.aircraft_model_id)
        if not model:
            raise NotFoundError("Modelo de avión", inspection.aircraft_model_id)
        return inspection, model

    def _get_annotation_or_raise(self, inspection_id: int, annotation_id: int) -> Model3DAnnotation:
        annotation = self._annotations.get_by_id(inspection_id, annotation_id)
        if not annotation:
            raise NotFoundError("Anotación 3D", annotation_id)
        return annotation
