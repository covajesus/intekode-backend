"""Dependency injection container — wires repositories and services per request."""

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.application.services.aircraft_model_service import AircraftModelService
from app.application.services.photo_annotation_service import PhotoAnnotationService
from app.application.services.model3d_annotation_service import Model3DAnnotationService
from app.application.services.auth_service import AuthService
from app.application.services.inspection_service import InspectionService
from app.application.services.inspection_report_service import InspectionReportService
from app.core.exceptions import AuthenticationError
from app.core.security import password_hasher, token_service
from app.domain.tenant_context import TenantContext
from app.infrastructure.database.session import get_db_session
from app.infrastructure.persistence.models.user import User
from app.infrastructure.persistence.repositories.aircraft_model_repository import (
    SqlAlchemyAircraftModelRepository,
)
from app.infrastructure.persistence.repositories.inspection_repository import (
    SqlAlchemyInspectionRepository,
)
from app.infrastructure.persistence.repositories.organization_repository import (
    SqlAlchemyOrganizationRepository,
)
from app.infrastructure.persistence.repositories.photo_annotation_repository import (
    SqlAlchemyPhotoAnnotationRepository,
)
from app.infrastructure.persistence.repositories.model3d_annotation_repository import (
    SqlAlchemyModel3DAnnotationRepository,
)
from app.infrastructure.persistence.repositories.user_repository import SqlAlchemyUserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_user_repository(session: Session = Depends(get_db_session)) -> SqlAlchemyUserRepository:
    return SqlAlchemyUserRepository(session)


def get_organization_repository(
    session: Session = Depends(get_db_session),
) -> SqlAlchemyOrganizationRepository:
    return SqlAlchemyOrganizationRepository(session)


def get_inspection_repository(
    session: Session = Depends(get_db_session),
) -> SqlAlchemyInspectionRepository:
    return SqlAlchemyInspectionRepository(session)


def get_auth_service(
    user_repo: SqlAlchemyUserRepository = Depends(get_user_repository),
    organization_repo: SqlAlchemyOrganizationRepository = Depends(get_organization_repository),
) -> AuthService:
    return AuthService(user_repo, organization_repo, password_hasher, token_service)


def get_aircraft_model_repository(
    session: Session = Depends(get_db_session),
) -> SqlAlchemyAircraftModelRepository:
    return SqlAlchemyAircraftModelRepository(session)


def get_photo_annotation_repository(
    session: Session = Depends(get_db_session),
) -> SqlAlchemyPhotoAnnotationRepository:
    return SqlAlchemyPhotoAnnotationRepository(session)


def get_photo_annotation_service(
    inspection_repo: SqlAlchemyInspectionRepository = Depends(get_inspection_repository),
    aircraft_model_repo: SqlAlchemyAircraftModelRepository = Depends(get_aircraft_model_repository),
    annotation_repo: SqlAlchemyPhotoAnnotationRepository = Depends(get_photo_annotation_repository),
) -> PhotoAnnotationService:
    return PhotoAnnotationService(inspection_repo, aircraft_model_repo, annotation_repo)


def get_model3d_annotation_repository(
    session: Session = Depends(get_db_session),
) -> SqlAlchemyModel3DAnnotationRepository:
    return SqlAlchemyModel3DAnnotationRepository(session)


def get_model3d_annotation_service(
    inspection_repo: SqlAlchemyInspectionRepository = Depends(get_inspection_repository),
    aircraft_model_repo: SqlAlchemyAircraftModelRepository = Depends(get_aircraft_model_repository),
    annotation_repo: SqlAlchemyModel3DAnnotationRepository = Depends(
        get_model3d_annotation_repository
    ),
) -> Model3DAnnotationService:
    return Model3DAnnotationService(inspection_repo, aircraft_model_repo, annotation_repo)


def get_aircraft_model_service(
    repository: SqlAlchemyAircraftModelRepository = Depends(get_aircraft_model_repository),
) -> AircraftModelService:
    return AircraftModelService(repository)


def get_inspection_service(
    inspection_repo: SqlAlchemyInspectionRepository = Depends(get_inspection_repository),
    aircraft_model_repo: SqlAlchemyAircraftModelRepository = Depends(get_aircraft_model_repository),
) -> InspectionService:
    return InspectionService(inspection_repo, aircraft_model_repo)


def get_inspection_report_service(
    inspection_service: InspectionService = Depends(get_inspection_service),
) -> InspectionReportService:
    return InspectionReportService(inspection_service)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    payload = token_service.decode_token(token)
    if not payload or "sub" not in payload:
        raise AuthenticationError("Token inválido o expirado")
    return auth_service.get_user_by_username(payload["sub"])


def get_tenant_context(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service),
) -> TenantContext:
    payload = token_service.decode_token(token)
    if not payload or "sub" not in payload or "org_id" not in payload:
        raise AuthenticationError("Token inválido o expirado")

    user = auth_service.get_user_by_username(payload["sub"])
    organization = auth_service.resolve_tenant(user, int(payload["org_id"]))

    return TenantContext(
        organization_id=organization.id,
        organization_name=organization.name,
        organization_slug=organization.slug,
        role=organization.role,
        user=user,
    )
