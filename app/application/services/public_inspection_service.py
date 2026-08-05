"""Public read-only service for shared 3D inspection links."""

from app.application.dto.public_inspection import (
    PublicModel3DFindingDTO,
    PublicModel3DViewDTO,
)
from app.core.exceptions import NotFoundError
from app.domain.interfaces.repositories import (
    IAircraftModelRepository,
    IInspectionRepository,
    IModel3DAnnotationRepository,
)
from app.infrastructure.storage.file_storage_service import (
    FileStorageService,
    file_storage_service,
)


class PublicInspectionService:
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

    def get_model3d_view(self, token: str) -> PublicModel3DViewDTO:
        inspection, model = self._resolve_by_token(token)
        annotations = self._annotations.list_by_inspection(inspection.id)
        findings = [
            PublicModel3DFindingDTO(
                id=annotation.id,
                number=index + 1,
                annotation_type=annotation.annotation_type,
                x=annotation.x,
                y=annotation.y,
                z=annotation.z,
                x2=annotation.x2,
                y2=annotation.y2,
                z2=annotation.z2,
                color=annotation.color,
                section_label=annotation.section_label,
                title=annotation.title,
                notes=annotation.notes,
            )
            for index, annotation in enumerate(annotations)
        ]
        return PublicModel3DViewDTO(
            registration=inspection.registration,
            aircraft_model=inspection.aircraft_model,
            has_glb=bool(model and model.glb_file_path),
            glb_original_name=(model.glb_original_name if model else None),
            finding_count=len(findings),
            findings=findings,
        )

    def get_glb_file_path(self, token: str) -> tuple[str, str]:
        _, model = self._resolve_by_token(token)
        if not model or not model.glb_file_path:
            raise NotFoundError("Modelo 3D (GLB)", token)

        absolute = self._storage.resolve_absolute_path(model.glb_file_path)
        if not absolute.exists() or not absolute.is_file():
            raise NotFoundError("Archivo GLB", token)

        filename = model.glb_original_name or model.glb_file_name or "model.glb"
        return str(absolute), filename

    def _resolve_by_token(self, token: str):
        inspection = self._inspections.get_by_public_share_token(token)
        if not inspection:
            raise NotFoundError("Enlace público", token)

        model = None
        if inspection.aircraft_model_id:
            model = self._aircraft_models.get_by_id(
                inspection.organization_id,
                inspection.aircraft_model_id,
            )
        return inspection, model
