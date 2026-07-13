"""Inspection endpoints — thin controller layer delegating to InspectionService."""

from io import BytesIO

from fastapi import APIRouter, Depends, status
from fastapi.responses import StreamingResponse

from app.api.dependencies import (
    get_inspection_report_service,
    get_inspection_service,
    get_tenant_context,
)
from app.application.dto.inspection import (
    InspectionCreateDTO,
    InspectionResponseDTO,
    InspectionSummaryDTO,
    InspectionTemplateDTO,
    InspectionUpdateDTO,
)
from app.application.services.inspection_report_service import InspectionReportService
from app.application.services.inspection_service import InspectionService
from app.domain.tenant_context import TenantContext

router = APIRouter(prefix="/api/inspections", tags=["Inspections"])


@router.get("/template", response_model=InspectionTemplateDTO, summary="Inspection form template")
def get_template(
    _: TenantContext = Depends(get_tenant_context),
    service: InspectionService = Depends(get_inspection_service),
) -> InspectionTemplateDTO:
    return service.get_template()


@router.get("", response_model=list[InspectionSummaryDTO], summary="List inspections for active client")
def list_inspections(
    tenant: TenantContext = Depends(get_tenant_context),
    service: InspectionService = Depends(get_inspection_service),
) -> list[InspectionSummaryDTO]:
    return service.list_inspections(tenant.organization_id)


@router.post(
    "",
    response_model=InspectionResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create inspection",
)
def create_inspection(
    payload: InspectionCreateDTO,
    tenant: TenantContext = Depends(get_tenant_context),
    service: InspectionService = Depends(get_inspection_service),
) -> InspectionResponseDTO:
    return service.create_inspection(
        payload,
        created_by=tenant.user.id,
        organization_id=tenant.organization_id,
    )


@router.get(
    "/{inspection_id}/pdf",
    summary="Download inspection PDF report",
    response_class=StreamingResponse,
)
def download_inspection_pdf(
    inspection_id: int,
    tenant: TenantContext = Depends(get_tenant_context),
    report_service: InspectionReportService = Depends(get_inspection_report_service),
) -> StreamingResponse:
    pdf_bytes, filename = report_service.build_pdf(tenant.organization_id, inspection_id)
    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"',
    }
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers=headers,
    )


@router.get("/{inspection_id}", response_model=InspectionResponseDTO, summary="Get inspection by ID")
def get_inspection(
    inspection_id: int,
    tenant: TenantContext = Depends(get_tenant_context),
    service: InspectionService = Depends(get_inspection_service),
) -> InspectionResponseDTO:
    return service.get_inspection(tenant.organization_id, inspection_id)


@router.put("/{inspection_id}", response_model=InspectionResponseDTO, summary="Update inspection")
def update_inspection(
    inspection_id: int,
    payload: InspectionUpdateDTO,
    tenant: TenantContext = Depends(get_tenant_context),
    service: InspectionService = Depends(get_inspection_service),
) -> InspectionResponseDTO:
    return service.update_inspection(tenant.organization_id, inspection_id, payload)


@router.delete("/{inspection_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete inspection")
def delete_inspection(
    inspection_id: int,
    tenant: TenantContext = Depends(get_tenant_context),
    service: InspectionService = Depends(get_inspection_service),
) -> None:
    service.delete_inspection(tenant.organization_id, inspection_id)
