"""Database seed — default SaaS client and admin user."""

from app.core.security import password_hasher
from app.domain.enums import OrganizationRole
from app.infrastructure.database.base import Base
from app.infrastructure.database.session import SessionLocal, engine
from app.infrastructure.persistence.models.organization import Organization, OrganizationMember
from app.infrastructure.persistence.models.user import User
from app.infrastructure.persistence.repositories.organization_repository import (
    SqlAlchemyOrganizationRepository,
)
from app.infrastructure.persistence.repositories.user_repository import SqlAlchemyUserRepository

# Register all ORM models before create_all
import app.infrastructure.persistence.models.aircraft_model  # noqa: F401
import app.infrastructure.persistence.models.inspection  # noqa: F401
import app.infrastructure.persistence.models.organization  # noqa: F401
import app.infrastructure.persistence.models.user  # noqa: F401

DEFAULT_ORG_NAME = "Cliente Demo"
DEFAULT_ORG_SLUG = "demo"


def seed_admin() -> None:
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    user_repo = SqlAlchemyUserRepository(session)
    org_repo = SqlAlchemyOrganizationRepository(session)

    try:
        organization = org_repo.find_by_slug(DEFAULT_ORG_SLUG)
        if not organization:
            organization = Organization(name=DEFAULT_ORG_NAME, slug=DEFAULT_ORG_SLUG)
            org_repo.create(organization)
            org_repo.commit()
            organization = org_repo.refresh(organization)
            print(f"Cliente creado: {organization.name} ({organization.slug})")

        admin = user_repo.find_by_username("admin")
        if not admin:
            admin = User(
                username="admin",
                email="admin@aviacion.com",
                full_name="Administrador",
                hashed_password=password_hasher.hash("123"),
            )
            user_repo.create(admin)
            user_repo.commit()
            admin = user_repo.refresh(admin)
            print("Usuario admin creado: admin / 123")
        else:
            admin.hashed_password = password_hasher.hash("123")
            admin.email = "admin@aviacion.com"
            user_repo.commit()
            print("Usuario admin actualizado: admin / 123")

        membership = org_repo.get_membership(organization.id, admin.id)
        if not membership:
            org_repo.create_member(
                OrganizationMember(
                    organization_id=organization.id,
                    user_id=admin.id,
                    role=OrganizationRole.ADMIN,
                )
            )
            org_repo.commit()
            print(f"Admin vinculado al cliente {organization.name}")
    finally:
        session.close()


if __name__ == "__main__":
    from scripts.migrate_inspection_annotations import migrate as migrate_inspection_annotations
    from scripts.migrate_multitenancy import migrate

    seed_admin()
    migrate()
    migrate_inspection_annotations()

    from scripts.migrate_aircraft_model_components import (
        migrate as migrate_aircraft_model_components,
    )

    migrate_aircraft_model_components()
