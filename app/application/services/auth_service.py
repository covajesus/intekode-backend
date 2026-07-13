"""Authentication application service — orchestrates auth use cases."""

import re

from app.application.dto.auth import (
    LoginRequestDTO,
    MeResponseDTO,
    OrganizationSummaryDTO,
    TokenDTO,
    UserCreateDTO,
    UserResponseDTO,
)
from app.core.exceptions import AuthenticationError, AuthorizationError, ConflictError
from app.core.security import PasswordHasher, TokenService
from app.domain.enums import OrganizationRole
from app.domain.interfaces.repositories import IOrganizationRepository, IUserRepository
from app.infrastructure.persistence.models.organization import Organization, OrganizationMember
from app.infrastructure.persistence.models.user import User


class AuthService:
    def __init__(
        self,
        user_repository: IUserRepository,
        organization_repository: IOrganizationRepository,
        password_hasher: PasswordHasher,
        token_service: TokenService,
    ) -> None:
        self._users = user_repository
        self._organizations = organization_repository
        self._hasher = password_hasher
        self._tokens = token_service

    def login(self, credentials: LoginRequestDTO) -> TokenDTO:
        user = self._users.find_by_username(credentials.username)
        if not user or not self._hasher.verify(credentials.password, user.hashed_password):
            raise AuthenticationError()
        if not user.is_active:
            raise AuthenticationError("Usuario inactivo")

        membership = self._resolve_membership(user.id, credentials.organization_id)
        token = self._tokens.create_access_token(
            subject=user.username,
            organization_id=membership.organization_id,
            role=membership.role,
        )
        return TokenDTO(access_token=token)

    def switch_organization(self, user: User, organization_id: int) -> TokenDTO:
        membership = self._resolve_membership(user.id, organization_id)
        token = self._tokens.create_access_token(
            subject=user.username,
            organization_id=membership.organization_id,
            role=membership.role,
        )
        return TokenDTO(access_token=token)

    def register(self, payload: UserCreateDTO) -> User:
        existing = self._users.find_by_username_or_email(payload.username, payload.email)
        if existing:
            raise ConflictError("Usuario o email ya registrado")

        user = User(
            username=payload.username,
            email=payload.email,
            full_name=payload.full_name,
            hashed_password=self._hasher.hash(payload.password),
        )
        self._users.create(user)
        self._users.commit()
        user = self._users.refresh(user)

        if payload.organization_name:
            organization = Organization(
                name=payload.organization_name.strip(),
                slug=self._build_unique_slug(payload.organization_name),
            )
            self._organizations.create(organization)
            self._organizations.commit()
            organization = self._organizations.refresh(organization)
            self._organizations.create_member(
                OrganizationMember(
                    organization_id=organization.id,
                    user_id=user.id,
                    role=OrganizationRole.ADMIN,
                )
            )
            self._organizations.commit()

        return user

    def get_user_by_username(self, username: str) -> User:
        user = self._users.find_by_username(username)
        if not user or not user.is_active:
            raise AuthenticationError("Usuario no autorizado")
        return user

    def build_me_response(self, user: User, *, organization_id: int) -> MeResponseDTO:
        memberships = self._organizations.list_memberships_for_user(user.id)
        if not memberships:
            raise AuthorizationError("El usuario no pertenece a ningún cliente")

        organizations = [
            OrganizationSummaryDTO(
                id=membership.organization.id,
                name=membership.organization.name,
                slug=membership.organization.slug,
                role=membership.role,
            )
            for membership in memberships
        ]

        current = next((org for org in organizations if org.id == organization_id), None)
        if not current:
            raise AuthorizationError("Cliente no autorizado para este usuario")

        return MeResponseDTO(
            user=UserResponseDTO.model_validate(user),
            organization=current,
            organizations=organizations,
        )

    def resolve_tenant(self, user: User, organization_id: int) -> OrganizationSummaryDTO:
        membership = self._organizations.get_membership(organization_id, user.id)
        if not membership:
            raise AuthorizationError("No tiene acceso a este cliente")

        organization = self._organizations.get_by_id(organization_id)
        if not organization:
            raise AuthorizationError("Cliente inactivo o inexistente")

        return OrganizationSummaryDTO(
            id=organization.id,
            name=organization.name,
            slug=organization.slug,
            role=membership.role,
        )

    def _resolve_membership(
        self,
        user_id: int,
        organization_id: int | None,
    ) -> OrganizationMember:
        memberships = self._organizations.list_memberships_for_user(user_id)
        if not memberships:
            raise AuthorizationError("El usuario no pertenece a ningún cliente")

        if organization_id is not None:
            membership = self._organizations.get_membership(organization_id, user_id)
            if not membership:
                raise AuthorizationError("No tiene acceso a este cliente")
            return membership

        if len(memberships) == 1:
            return memberships[0]

        raise AuthenticationError("Debe seleccionar un cliente para iniciar sesión")

    def _build_unique_slug(self, name: str) -> str:
        base = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "cliente"
        slug = base
        suffix = 1
        while self._organizations.find_by_slug(slug):
            suffix += 1
            slug = f"{base}-{suffix}"
        return slug
