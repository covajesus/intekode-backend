"""Inspection 3D model annotation endpoints — mark findings on the aircraft GLB."""

from fastapi import APIRouter, Depends, status
from fastapi.responses import FileResponse

from app.api.dependencies import get_model3d_annotation_service, get_tenant_context
from app.application.dto.model3d_annotation import (
    Model3DAnnotationCreateDTO,
    Model3DAnnotationResponseDTO,
    Model3DAnnotationUpdateDTO,
    Model3DWithAnnotationsDTO,
)
from app.application.services.model3d_annotation_service import Model3DAnnotationService
from app.domain.tenant_context import TenantContext

router = APIRouter(
    prefix="/api/inspections/{inspection_id}/model3d",
    tags=["Inspection 3D Model Annotations"],
)


@router.get(
    "",
    response_model=Model3DWithAnnotationsDTO,
    summary="Get aircraft GLB with inspection 3D annotations",
)
def get_model3d_with_annotations(
    inspection_id: int,
    tenant: TenantContext = Depends(get_tenant_context),
    service: Model3DAnnotationService = Depends(get_model3d_annotation_service),
) -> Model3DWithAnnotationsDTO:
    return service.get_model_with_annotations(tenant.organization_id, inspection_id)


@router.get(
    "/file",
    summary="Download aircraft GLB for inspection viewer",
    response_class=FileResponse,
)
def download_model3d_file(
    inspection_id: int,
    tenant: TenantContext = Depends(get_tenant_context),
    service: Model3DAnnotationService = Depends(get_model3d_annotation_service),
) -> FileResponse:
    path, filename = service.get_glb_file_path(tenant.organization_id, inspection_id)
    return FileResponse(
        path,
        media_type="model/gltf-binary",
        filename=filename,
        headers={"Cache-Control": "private, max-age=300"},
    )


@router.post(
    "/annotations",
    response_model=Model3DAnnotationResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create 3D annotation on inspection GLB",
)
def create_model3d_annotation(
    inspection_id: int,
    payload: Model3DAnnotationCreateDTO,
    tenant: TenantContext = Depends(get_tenant_context),
    service: Model3DAnnotationService = Depends(get_model3d_annotation_service),
) -> Model3DAnnotationResponseDTO:
    return service.create_annotation(tenant.organization_id, inspection_id, payload)


@router.put(
    "/annotations/{annotation_id}",
    response_model=Model3DAnnotationResponseDTO,
    summary="Update inspection 3D annotation",
)
def update_model3d_annotation(
    inspection_id: int,
    annotation_id: int,
    payload: Model3DAnnotationUpdateDTO,
    tenant: TenantContext = Depends(get_tenant_context),
    service: Model3DAnnotationService = Depends(get_model3d_annotation_service),
) -> Model3DAnnotationResponseDTO:
    return service.update_annotation(
        tenant.organization_id,
        inspection_id,
        annotation_id,
        payload,
    )


@router.delete(
    "/annotations/{annotation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete inspection 3D annotation",
)
def delete_model3d_annotation(
    inspection_id: int,
    annotation_id: int,
    tenant: TenantContext = Depends(get_tenant_context),
    service: Model3DAnnotationService = Depends(get_model3d_annotation_service),
) -> None:
    service.delete_annotation(tenant.organization_id, inspection_id, annotation_id)
