"""Inspection application service — business logic for inspection lifecycle."""

from app.application.dto.inspection import (
    InspectionCreateDTO,
    InspectionTemplateDTO,
    InspectionUpdateDTO,
)
from app.application.mappers.inspection_mapper import InspectionMapper
from app.application.services.inspection_template_service import InspectionTemplateFactory
from app.application.utils.aircraft_model_formatter import format_inspection_model_name
from app.core.exceptions import NotFoundError
from app.domain.interfaces.repositories import IAircraftModelRepository, IInspectionRepository
from app.infrastructure.persistence.models.inspection import Inspection


class InspectionService:
    def __init__(
        self,
        inspection_repository: IInspectionRepository,
        aircraft_model_repository: IAircraftModelRepository | None = None,
    ) -> None:
        self._repository = inspection_repository
        self._aircraft_models = aircraft_model_repository

    def get_template(self) -> InspectionTemplateDTO:
        return InspectionTemplateFactory.build()

    def list_inspections(self, organization_id: int) -> list[Inspection]:
        return self._repository.list_by_organization(organization_id)

    def get_inspection(self, organization_id: int, inspection_id: int) -> Inspection:
        inspection = self._repository.get_by_id(organization_id, inspection_id)
        if not inspection:
            raise NotFoundError("Inspección", inspection_id)
        return inspection

    def create_inspection(
        self,
        payload: InspectionCreateDTO,
        *,
        created_by: int,
        organization_id: int,
    ) -> Inspection:
        resolved = self._resolve_catalog_link(payload, organization_id)
        inspection = InspectionMapper.to_entity(
            resolved,
            created_by=created_by,
            organization_id=organization_id,
        )
        self._repository.create(inspection)
        self._repository.commit()
        return self._repository.refresh(inspection)

    def update_inspection(
        self,
        organization_id: int,
        inspection_id: int,
        payload: InspectionUpdateDTO,
    ) -> Inspection:
        inspection = self.get_inspection(organization_id, inspection_id)
        resolved = self._resolve_catalog_link(payload, organization_id)
        InspectionMapper.apply_update(inspection, resolved)
        self._repository.commit()
        return self._repository.refresh(inspection)

    def delete_inspection(self, organization_id: int, inspection_id: int) -> None:
        inspection = self.get_inspection(organization_id, inspection_id)
        self._repository.delete(inspection)
        self._repository.commit()

    def _resolve_catalog_link(
        self,
        payload: InspectionCreateDTO | InspectionUpdateDTO,
        organization_id: int,
    ) -> InspectionCreateDTO | InspectionUpdateDTO:
        if not self._aircraft_models or payload.aircraft_model_id is None:
            return payload

        catalog_model = self._aircraft_models.get_by_id(organization_id, payload.aircraft_model_id)
        if not catalog_model:
            raise NotFoundError("Modelo de avión", payload.aircraft_model_id)

        payload.aircraft_model = format_inspection_model_name(catalog_model)
        return payload
