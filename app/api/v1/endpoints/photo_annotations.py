"""Inspection photo annotation endpoints — mark sections during physical inspection."""

from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_photo_annotation_service, get_tenant_context
from app.application.dto.photo_annotation import (
    InspectionPhotoSummaryDTO,
    PhotoAnnotationCreateDTO,
    PhotoAnnotationResponseDTO,
    PhotoAnnotationUpdateDTO,
    PhotoWithAnnotationsDTO,
)
from app.application.services.photo_annotation_service import PhotoAnnotationService
from app.domain.tenant_context import TenantContext

router = APIRouter(
    prefix="/api/inspections/{inspection_id}/photos",
    tags=["Inspection Photo Annotations"],
)


@router.get("", response_model=list[InspectionPhotoSummaryDTO], summary="List photos for inspection")
def list_inspection_photos(
    inspection_id: int,
    tenant: TenantContext = Depends(get_tenant_context),
    service: PhotoAnnotationService = Depends(get_photo_annotation_service),
) -> list[InspectionPhotoSummaryDTO]:
    return service.list_inspection_photos(tenant.organization_id, inspection_id)


@router.get(
    "/{photo_id}/annotations",
    response_model=PhotoWithAnnotationsDTO,
    summary="Get photo with inspection annotations",
)
def get_photo_annotations(
    inspection_id: int,
    photo_id: int,
    tenant: TenantContext = Depends(get_tenant_context),
    service: PhotoAnnotationService = Depends(get_photo_annotation_service),
) -> PhotoWithAnnotationsDTO:
    return service.get_photo_with_annotations(tenant.organization_id, inspection_id, photo_id)


@router.post(
    "/{photo_id}/annotations",
    response_model=PhotoAnnotationResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create annotation on inspection photo",
)
def create_photo_annotation(
    inspection_id: int,
    photo_id: int,
    payload: PhotoAnnotationCreateDTO,
    tenant: TenantContext = Depends(get_tenant_context),
    service: PhotoAnnotationService = Depends(get_photo_annotation_service),
) -> PhotoAnnotationResponseDTO:
    return service.create_annotation(tenant.organization_id, inspection_id, photo_id, payload)


@router.put(
    "/{photo_id}/annotations/{annotation_id}",
    response_model=PhotoAnnotationResponseDTO,
    summary="Update inspection photo annotation",
)
def update_photo_annotation(
    inspection_id: int,
    photo_id: int,
    annotation_id: int,
    payload: PhotoAnnotationUpdateDTO,
    tenant: TenantContext = Depends(get_tenant_context),
    service: PhotoAnnotationService = Depends(get_photo_annotation_service),
) -> PhotoAnnotationResponseDTO:
    return service.update_annotation(
        tenant.organization_id,
        inspection_id,
        photo_id,
        annotation_id,
        payload,
    )


@router.delete(
    "/{photo_id}/annotations/{annotation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete inspection photo annotation",
)
def delete_photo_annotation(
    inspection_id: int,
    photo_id: int,
    annotation_id: int,
    tenant: TenantContext = Depends(get_tenant_context),
    service: PhotoAnnotationService = Depends(get_photo_annotation_service),
) -> None:
    service.delete_annotation(tenant.organization_id, inspection_id, photo_id, annotation_id)
