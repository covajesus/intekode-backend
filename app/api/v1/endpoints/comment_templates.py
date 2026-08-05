"""Tenant-scoped reusable comment template endpoints."""

from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_comment_template_service, get_tenant_context
from app.application.dto.comment_template import (
    CommentTemplateCreateDTO,
    CommentTemplateResponseDTO,
    CommentTemplateUpdateDTO,
)
from app.application.services.comment_template_service import CommentTemplateService
from app.domain.tenant_context import TenantContext

router = APIRouter(prefix="/api/comment-templates", tags=["Comment Templates"])


@router.get("", response_model=list[CommentTemplateResponseDTO])
def list_comment_templates(
    tenant: TenantContext = Depends(get_tenant_context),
    service: CommentTemplateService = Depends(get_comment_template_service),
) -> list[CommentTemplateResponseDTO]:
    return service.list_templates(tenant.organization_id)


@router.post(
    "",
    response_model=CommentTemplateResponseDTO,
    status_code=status.HTTP_201_CREATED,
)
def create_comment_template(
    payload: CommentTemplateCreateDTO,
    tenant: TenantContext = Depends(get_tenant_context),
    service: CommentTemplateService = Depends(get_comment_template_service),
) -> CommentTemplateResponseDTO:
    return service.create_template(tenant.organization_id, payload)


@router.get("/{template_id}", response_model=CommentTemplateResponseDTO)
def get_comment_template(
    template_id: int,
    tenant: TenantContext = Depends(get_tenant_context),
    service: CommentTemplateService = Depends(get_comment_template_service),
) -> CommentTemplateResponseDTO:
    return service.get_template(tenant.organization_id, template_id)


@router.put("/{template_id}", response_model=CommentTemplateResponseDTO)
def update_comment_template(
    template_id: int,
    payload: CommentTemplateUpdateDTO,
    tenant: TenantContext = Depends(get_tenant_context),
    service: CommentTemplateService = Depends(get_comment_template_service),
) -> CommentTemplateResponseDTO:
    return service.update_template(tenant.organization_id, template_id, payload)


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment_template(
    template_id: int,
    tenant: TenantContext = Depends(get_tenant_context),
    service: CommentTemplateService = Depends(get_comment_template_service),
) -> None:
    service.delete_template(tenant.organization_id, template_id)
