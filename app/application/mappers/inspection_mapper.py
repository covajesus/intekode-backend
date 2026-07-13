"""Inspection mapper — translates DTOs to ORM aggregates (Mapper pattern)."""

from app.application.dto.inspection import (
    InspectionCreateDTO,
    InspectionUpdateDTO,
)
from app.infrastructure.persistence.models.inspection import (
    ChecklistItem,
    ComponentSerial,
    Discrepancy,
    Inspection,
)


class InspectionMapper:
    """Maps inspection DTOs to domain/persistence models."""

    @staticmethod
    def to_entity(
        dto: InspectionCreateDTO,
        *,
        created_by: int,
        organization_id: int,
    ) -> Inspection:
        scalar_data = dto.model_dump(
            exclude={"component_serials", "checklist_items", "discrepancies"}
        )
        inspection = Inspection(
            **scalar_data,
            created_by=created_by,
            organization_id=organization_id,
        )
        InspectionMapper.apply_nested_collections(inspection, dto)
        return inspection

    @staticmethod
    def apply_update(entity: Inspection, dto: InspectionUpdateDTO) -> None:
        update_data = dto.model_dump(
            exclude_unset=True,
            exclude={"component_serials", "checklist_items", "discrepancies"},
        )
        for key, value in update_data.items():
            setattr(entity, key, value)
        InspectionMapper.apply_nested_collections(entity, dto)

    @staticmethod
    def apply_nested_collections(
        entity: Inspection,
        dto: InspectionCreateDTO | InspectionUpdateDTO,
    ) -> None:
        if dto.component_serials is not None:
            entity.component_serials.clear()
            entity.component_serials.extend(
                ComponentSerial(**item.model_dump()) for item in dto.component_serials
            )

        if dto.checklist_items is not None:
            entity.checklist_items.clear()
            entity.checklist_items.extend(
                ChecklistItem(**item.model_dump()) for item in dto.checklist_items
            )

        if dto.discrepancies is not None:
            entity.discrepancies.clear()
            entity.discrepancies.extend(
                Discrepancy(**item.model_dump()) for item in dto.discrepancies
            )
