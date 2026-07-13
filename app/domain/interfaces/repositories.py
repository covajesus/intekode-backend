"""Repository contracts — Dependency Inversion (interfaces consumed by services)."""

from abc import ABC, abstractmethod

from app.infrastructure.persistence.models.aircraft_model import (
    AircraftModel,
    AircraftModelPhoto,
    PhotoAnnotation,
)
from app.infrastructure.persistence.models.inspection import Inspection
from app.infrastructure.persistence.models.organization import Organization, OrganizationMember
from app.infrastructure.persistence.models.user import User


class IOrganizationRepository(ABC):
    @abstractmethod
    def get_by_id(self, organization_id: int) -> Organization | None: ...

    @abstractmethod
    def find_by_slug(self, slug: str) -> Organization | None: ...

    @abstractmethod
    def create(self, organization: Organization) -> Organization: ...

    @abstractmethod
    def create_member(self, member: OrganizationMember) -> OrganizationMember: ...

    @abstractmethod
    def get_membership(self, organization_id: int, user_id: int) -> OrganizationMember | None: ...

    @abstractmethod
    def list_memberships_for_user(self, user_id: int) -> list[OrganizationMember]: ...

    @abstractmethod
    def commit(self) -> None: ...

    @abstractmethod
    def refresh(self, entity): ...


class IUserRepository(ABC):
    @abstractmethod
    def find_by_username(self, username: str) -> User | None: ...

    @abstractmethod
    def find_by_username_or_email(self, username: str, email: str) -> User | None: ...

    @abstractmethod
    def create(self, user: User) -> User: ...

    @abstractmethod
    def commit(self) -> None: ...

    @abstractmethod
    def refresh(self, entity: User) -> User: ...


class IInspectionRepository(ABC):
    @abstractmethod
    def list_by_organization(self, organization_id: int) -> list[Inspection]: ...

    @abstractmethod
    def get_by_id(self, organization_id: int, inspection_id: int) -> Inspection | None: ...

    @abstractmethod
    def create(self, inspection: Inspection) -> Inspection: ...

    @abstractmethod
    def delete(self, inspection: Inspection) -> None: ...

    @abstractmethod
    def commit(self) -> None: ...

    @abstractmethod
    def refresh(self, entity: Inspection) -> Inspection: ...


class IAircraftModelRepository(ABC):
    @abstractmethod
    def list_by_organization(self, organization_id: int) -> list[AircraftModel]: ...

    @abstractmethod
    def get_by_id(self, organization_id: int, model_id: int) -> AircraftModel | None: ...

    @abstractmethod
    def create(self, model: AircraftModel) -> AircraftModel: ...

    @abstractmethod
    def delete(self, model: AircraftModel) -> None: ...

    @abstractmethod
    def add_photo(self, photo: AircraftModelPhoto) -> AircraftModelPhoto: ...

    @abstractmethod
    def get_photo(self, model_id: int, photo_id: int) -> AircraftModelPhoto | None: ...

    @abstractmethod
    def delete_photo(self, photo: AircraftModelPhoto) -> None: ...

    @abstractmethod
    def clear_primary_photos(self, model_id: int) -> None: ...

    @abstractmethod
    def commit(self) -> None: ...

    @abstractmethod
    def refresh(self, entity): ...


class IPhotoAnnotationRepository(ABC):
    @abstractmethod
    def list_by_inspection_photo(self, inspection_id: int, photo_id: int) -> list[PhotoAnnotation]: ...

    @abstractmethod
    def get_by_id(
        self, inspection_id: int, photo_id: int, annotation_id: int
    ) -> PhotoAnnotation | None: ...

    @abstractmethod
    def create(self, annotation: PhotoAnnotation) -> PhotoAnnotation: ...

    @abstractmethod
    def delete(self, annotation: PhotoAnnotation) -> None: ...

    @abstractmethod
    def commit(self) -> None: ...

    @abstractmethod
    def refresh(self, entity: PhotoAnnotation) -> PhotoAnnotation: ...
