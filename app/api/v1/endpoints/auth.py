"""Authentication endpoints — thin controller layer."""

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies import get_auth_service, get_current_user, get_tenant_context
from app.application.dto.auth import (
    LoginRequestDTO,
    MeResponseDTO,
    SwitchOrganizationDTO,
    TokenDTO,
    UserCreateDTO,
    UserResponseDTO,
)
from app.application.services.auth_service import AuthService
from app.domain.tenant_context import TenantContext
from app.infrastructure.persistence.models.user import User

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenDTO, summary="OAuth2 form login")
def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenDTO:
    return auth_service.login(LoginRequestDTO(username=form_data.username, password=form_data.password))


@router.post("/login/json", response_model=TokenDTO, summary="JSON login")
def login_json(
    payload: LoginRequestDTO,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenDTO:
    return auth_service.login(payload)


@router.get("/me", response_model=MeResponseDTO, summary="Current user and active client")
def get_me(
    tenant: TenantContext = Depends(get_tenant_context),
    auth_service: AuthService = Depends(get_auth_service),
) -> MeResponseDTO:
    return auth_service.build_me_response(tenant.user, organization_id=tenant.organization_id)


@router.post("/switch-organization", response_model=TokenDTO, summary="Switch active SaaS client")
def switch_organization(
    payload: SwitchOrganizationDTO,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenDTO:
    return auth_service.switch_organization(current_user, payload.organization_id)


@router.post(
    "/register",
    response_model=UserResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
)
def register(
    payload: UserCreateDTO,
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    return auth_service.register(payload)
