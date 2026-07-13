"""Organization repository — tenant membership and lookup."""

from sqlalchemy.orm import Session, joinedload

from app.domain.interfaces.repositories import IOrganizationRepository
from app.infrastructure.persistence.models.organization import Organization, OrganizationMember


class SqlAlchemyOrganizationRepository(IOrganizationRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, organization_id: int) -> Organization | None:
        return (
            self._session.query(Organization)
            .filter(Organization.id == organization_id, Organization.is_active.is_(True))
            .first()
        )

    def find_by_slug(self, slug: str) -> Organization | None:
        return (
            self._session.query(Organization)
            .filter(Organization.slug == slug)
            .first()
        )

    def create(self, organization: Organization) -> Organization:
        self._session.add(organization)
        return organization

    def create_member(self, member: OrganizationMember) -> OrganizationMember:
        self._session.add(member)
        return member

    def get_membership(self, organization_id: int, user_id: int) -> OrganizationMember | None:
        return (
            self._session.query(OrganizationMember)
            .filter(
                OrganizationMember.organization_id == organization_id,
                OrganizationMember.user_id == user_id,
            )
            .first()
        )

    def list_memberships_for_user(self, user_id: int) -> list[OrganizationMember]:
        return (
            self._session.query(OrganizationMember)
            .options(joinedload(OrganizationMember.organization))
            .join(Organization)
            .filter(
                OrganizationMember.user_id == user_id,
                Organization.is_active.is_(True),
            )
            .order_by(Organization.name)
            .all()
        )

    def commit(self) -> None:
        self._session.commit()

    def refresh(self, entity):
        self._session.refresh(entity)
        return entity
