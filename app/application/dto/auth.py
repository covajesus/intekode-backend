from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreateDTO(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    password: str = Field(min_length=6)
    organization_name: str | None = Field(
        default=None,
        min_length=2,
        description="Nombre del cliente/organización al registrarse",
    )


class UserResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    full_name: str
    is_active: bool
    created_at: datetime


class OrganizationSummaryDTO(BaseModel):
    id: int
    name: str
    slug: str
    role: str


class LoginRequestDTO(BaseModel):
    username: str
    password: str
    organization_id: int | None = None


class SwitchOrganizationDTO(BaseModel):
    organization_id: int


class TokenDTO(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MeResponseDTO(BaseModel):
    user: UserResponseDTO
    organization: OrganizationSummaryDTO
    organizations: list[OrganizationSummaryDTO]
