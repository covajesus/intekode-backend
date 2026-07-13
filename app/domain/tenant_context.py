from dataclasses import dataclass

from app.infrastructure.persistence.models.user import User


@dataclass(frozen=True)
class TenantContext:
    """Active SaaS tenant scope for the current request."""

    organization_id: int
    organization_name: str
    organization_slug: str
    role: str
    user: User
