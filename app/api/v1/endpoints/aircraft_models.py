"""Aircraft model endpoints."""

from fastapi import APIRouter, Depends, File, Form, UploadFile, status

from app.api.dependencies import get_aircraft_model_service, get_tenant_context
from app.application.dto.aircraft_model import (
    AircraftModelCreateDTO,
    AircraftModelResponseDTO,
    AircraftModelSummaryDTO,
    AircraftModelUpdateDTO,
)
from app.application.services.aircraft_model_service import AircraftModelService
from app.domain.tenant_context import TenantContext

router = APIRouter(prefix="/api/aircraft-models", tags=["Aircraft Models"])


@router.get("", response_model=list[AircraftModelSummaryDTO], summary="List aircraft models for active client")
def list_aircraft_models(
    tenant: TenantContext = Depends(get_tenant_context),
    service: AircraftModelService = Depends(get_aircraft_model_service),
) -> list[AircraftModelSummaryDTO]:
    return service.list_models(tenant.organization_id)


@router.post(
    "",
    response_model=AircraftModelResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create aircraft model",
)
def create_aircraft_model(
    payload: AircraftModelCreateDTO,
    tenant: TenantContext = Depends(get_tenant_context),
    service: AircraftModelService = Depends(get_aircraft_model_service),
) -> AircraftModelResponseDTO:
    return service.create_model(tenant.organization_id, payload)


@router.get("/{model_id}", response_model=AircraftModelResponseDTO, summary="Get aircraft model")
def get_aircraft_model(
    model_id: int,
    tenant: TenantContext = Depends(get_tenant_context),
    service: AircraftModelService = Depends(get_aircraft_model_service),
) -> AircraftModelResponseDTO:
    return service.get_model(tenant.organization_id, model_id)


@router.put("/{model_id}", response_model=AircraftModelResponseDTO, summary="Update aircraft model")
def update_aircraft_model(
    model_id: int,
    payload: AircraftModelUpdateDTO,
    tenant: TenantContext = Depends(get_tenant_context),
    service: AircraftModelService = Depends(get_aircraft_model_service),
) -> AircraftModelResponseDTO:
    return service.update_model(tenant.organization_id, model_id, payload)


@router.delete("/{model_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete aircraft model")
def delete_aircraft_model(
    model_id: int,
    tenant: TenantContext = Depends(get_tenant_context),
    service: AircraftModelService = Depends(get_aircraft_model_service),
) -> None:
    service.delete_model(tenant.organization_id, model_id)


@router.post(
    "/{model_id}/photos",
    response_model=AircraftModelResponseDTO,
    summary="Upload aircraft model photos",
)
async def upload_aircraft_model_photos(
    model_id: int,
    files: list[UploadFile] = File(...),
    caption: str | None = Form(default=None),
    set_primary: bool = Form(default=False),
    tenant: TenantContext = Depends(get_tenant_context),
    service: AircraftModelService = Depends(get_aircraft_model_service),
) -> AircraftModelResponseDTO:
    return await service.upload_photos(
        tenant.organization_id,
        model_id,
        files,
        caption=caption,
        set_primary=set_primary,
    )


@router.delete(
    "/{model_id}/photos/{photo_id}",
    response_model=AircraftModelResponseDTO,
    summary="Delete aircraft model photo",
)
def delete_aircraft_model_photo(
    model_id: int,
    photo_id: int,
    tenant: TenantContext = Depends(get_tenant_context),
    service: AircraftModelService = Depends(get_aircraft_model_service),
) -> AircraftModelResponseDTO:
    return service.delete_photo(tenant.organization_id, model_id, photo_id)


@router.patch(
    "/{model_id}/photos/{photo_id}/primary",
    response_model=AircraftModelResponseDTO,
    summary="Set primary photo",
)
def set_primary_aircraft_model_photo(
    model_id: int,
    photo_id: int,
    tenant: TenantContext = Depends(get_tenant_context),
    service: AircraftModelService = Depends(get_aircraft_model_service),
) -> AircraftModelResponseDTO:
    return service.set_primary_photo(tenant.organization_id, model_id, photo_id)


@router.post(
    "/{model_id}/glb",
    response_model=AircraftModelResponseDTO,
    summary="Upload or replace aircraft model GLB",
)
async def upload_aircraft_model_glb(
    model_id: int,
    file: UploadFile = File(...),
    tenant: TenantContext = Depends(get_tenant_context),
    service: AircraftModelService = Depends(get_aircraft_model_service),
) -> AircraftModelResponseDTO:
    return await service.upload_glb(tenant.organization_id, model_id, file)


@router.delete(
    "/{model_id}/glb",
    response_model=AircraftModelResponseDTO,
    summary="Delete aircraft model GLB",
)
def delete_aircraft_model_glb(
    model_id: int,
    tenant: TenantContext = Depends(get_tenant_context),
    service: AircraftModelService = Depends(get_aircraft_model_service),
) -> AircraftModelResponseDTO:
    return service.delete_glb(tenant.organization_id, model_id)
