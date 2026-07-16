"""Aircraft model application service."""

from fastapi import UploadFile

from app.application.dto.aircraft_model import (
    AircraftModelCreateDTO,
    AircraftModelPhotoResponseDTO,
    AircraftModelResponseDTO,
    AircraftModelSummaryDTO,
    AircraftModelUpdateDTO,
)
from app.core.exceptions import ApplicationError, NotFoundError
from app.domain.interfaces.repositories import IAircraftModelRepository
from app.infrastructure.persistence.models.aircraft_model import AircraftModel, AircraftModelPhoto
from app.infrastructure.storage.file_storage_service import FileStorageService, file_storage_service
from app.resources.checklist_template import DEFAULT_COMPONENTS, DEFAULT_SECTIONS


def _normalize_components(components: list[str] | None) -> list[str]:
    if not components:
        return list(DEFAULT_COMPONENTS)
    allowed = set(DEFAULT_COMPONENTS)
    return [item for item in components if item in allowed]


def _normalize_sections(sections: list[str] | None) -> list[str]:
    if not sections:
        return list(DEFAULT_SECTIONS)
    allowed = set(DEFAULT_SECTIONS)
    return [item for item in sections if item in allowed]


class AircraftModelService:
    def __init__(
        self,
        repository: IAircraftModelRepository,
        storage: FileStorageService | None = None,
    ) -> None:
        self._repository = repository
        self._storage = storage or file_storage_service

    def list_models(self, organization_id: int) -> list[AircraftModelSummaryDTO]:
        models = self._repository.list_by_organization(organization_id)
        return [self._to_summary(model) for model in models]

    def get_model(self, organization_id: int, model_id: int) -> AircraftModelResponseDTO:
        model = self._get_or_raise(organization_id, model_id)
        return self._to_response(model)

    def create_model(
        self,
        organization_id: int,
        payload: AircraftModelCreateDTO,
    ) -> AircraftModelResponseDTO:
        data = payload.model_dump()
        data["applicable_components"] = _normalize_components(data.get("applicable_components"))
        data["applicable_sections"] = _normalize_sections(data.get("applicable_sections"))
        model = AircraftModel(**data, organization_id=organization_id)
        self._repository.create(model)
        self._repository.commit()
        self._repository.refresh(model)
        return self._to_response(model)

    def update_model(
        self,
        organization_id: int,
        model_id: int,
        payload: AircraftModelUpdateDTO,
    ) -> AircraftModelResponseDTO:
        model = self._get_or_raise(organization_id, model_id)
        update_data = payload.model_dump(exclude_unset=True)
        if "applicable_components" in update_data:
            update_data["applicable_components"] = _normalize_components(
                update_data.get("applicable_components")
            )
        if "applicable_sections" in update_data:
            update_data["applicable_sections"] = _normalize_sections(
                update_data.get("applicable_sections")
            )
        for key, value in update_data.items():
            setattr(model, key, value)
        self._repository.commit()
        self._repository.refresh(model)
        return self._to_response(model)

    def delete_model(self, organization_id: int, model_id: int) -> None:
        model = self._get_or_raise(organization_id, model_id)
        for photo in list(model.photos):
            self._storage.delete_file(photo.file_path)
        self._storage.delete_model_directory(model_id)
        self._repository.delete(model)
        self._repository.commit()

    async def upload_photos(
        self,
        organization_id: int,
        model_id: int,
        files: list[UploadFile],
        *,
        caption: str | None = None,
        set_primary: bool = False,
    ) -> AircraftModelResponseDTO:
        model = self._get_or_raise(organization_id, model_id)
        if not files:
            raise ApplicationError("Debe enviar al menos una imagen")

        if set_primary:
            self._repository.clear_primary_photos(model_id)

        next_sort = max((photo.sort_order for photo in model.photos), default=-1) + 1
        has_primary = any(photo.is_primary for photo in model.photos)

        for index, file in enumerate(files):
            file_name, file_path = self._storage.save_aircraft_model_photo(
                model_id=model_id,
                file=file,
            )
            is_primary = set_primary and index == 0
            if not has_primary and index == 0 and not set_primary:
                is_primary = True
                has_primary = True

            photo = AircraftModelPhoto(
                aircraft_model_id=model_id,
                file_name=file_name,
                file_path=file_path,
                original_name=file.filename,
                caption=caption,
                is_primary=is_primary,
                sort_order=next_sort + index,
            )
            self._repository.add_photo(photo)

        self._repository.commit()
        refreshed = self._get_or_raise(organization_id, model_id)
        return self._to_response(refreshed)

    def delete_photo(
        self,
        organization_id: int,
        model_id: int,
        photo_id: int,
    ) -> AircraftModelResponseDTO:
        model = self._get_or_raise(organization_id, model_id)
        photo = self._repository.get_photo(model_id, photo_id)
        if not photo:
            raise NotFoundError("Foto", photo_id)

        was_primary = photo.is_primary
        self._storage.delete_file(photo.file_path)
        self._repository.delete_photo(photo)
        self._repository.commit()

        if was_primary:
            refreshed = self._get_or_raise(organization_id, model_id)
            if refreshed.photos:
                refreshed.photos[0].is_primary = True
                self._repository.commit()

        return self._to_response(self._get_or_raise(organization_id, model_id))

    def set_primary_photo(
        self,
        organization_id: int,
        model_id: int,
        photo_id: int,
    ) -> AircraftModelResponseDTO:
        model = self._get_or_raise(organization_id, model_id)
        photo = self._repository.get_photo(model_id, photo_id)
        if not photo:
            raise NotFoundError("Foto", photo_id)

        self._repository.clear_primary_photos(model_id)
        photo.is_primary = True
        self._repository.commit()
        return self._to_response(self._get_or_raise(organization_id, model_id))

    async def upload_glb(
        self,
        organization_id: int,
        model_id: int,
        file: UploadFile,
    ) -> AircraftModelResponseDTO:
        model = self._get_or_raise(organization_id, model_id)
        if model.glb_file_path:
            self._storage.delete_file(model.glb_file_path)

        file_name, file_path = self._storage.save_aircraft_model_glb(
            model_id=model_id,
            file=file,
        )
        model.glb_file_name = file_name
        model.glb_file_path = file_path
        model.glb_original_name = file.filename
        self._repository.commit()
        self._repository.refresh(model)
        return self._to_response(model)

    def delete_glb(
        self,
        organization_id: int,
        model_id: int,
    ) -> AircraftModelResponseDTO:
        model = self._get_or_raise(organization_id, model_id)
        if not model.glb_file_path:
            raise NotFoundError("Modelo 3D (GLB)", model_id)

        self._storage.delete_file(model.glb_file_path)
        model.glb_file_name = None
        model.glb_file_path = None
        model.glb_original_name = None
        self._repository.commit()
        self._repository.refresh(model)
        return self._to_response(model)

    def _get_or_raise(self, organization_id: int, model_id: int) -> AircraftModel:
        model = self._repository.get_by_id(organization_id, model_id)
        if not model:
            raise NotFoundError("Modelo de avión", model_id)
        return model

    def _to_summary(self, model: AircraftModel) -> AircraftModelSummaryDTO:
        primary = next((photo for photo in model.photos if photo.is_primary), None)
        if not primary and model.photos:
            primary = model.photos[0]

        return AircraftModelSummaryDTO(
            id=model.id,
            manufacturer=model.manufacturer,
            model_name=model.model_name,
            series=model.series,
            is_active=model.is_active,
            applicable_components=list(model.applicable_components or DEFAULT_COMPONENTS),
            applicable_sections=list(getattr(model, "applicable_sections", None) or DEFAULT_SECTIONS),
            photo_count=len(model.photos),
            primary_photo_url=self._storage.build_public_url(primary.file_path) if primary else None,
            has_glb=bool(model.glb_file_path),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_response(self, model: AircraftModel) -> AircraftModelResponseDTO:
        photos = [
            AircraftModelPhotoResponseDTO(
                id=photo.id,
                aircraft_model_id=photo.aircraft_model_id,
                file_name=photo.file_name,
                file_path=photo.file_path,
                original_name=photo.original_name,
                caption=photo.caption,
                is_primary=photo.is_primary,
                sort_order=photo.sort_order,
                created_at=photo.created_at,
                url=self._storage.build_public_url(photo.file_path),
            )
            for photo in model.photos
        ]
        glb_url = (
            self._storage.build_public_url(model.glb_file_path) if model.glb_file_path else None
        )
        return AircraftModelResponseDTO(
            id=model.id,
            manufacturer=model.manufacturer,
            model_name=model.model_name,
            series=model.series,
            description=model.description,
            is_active=model.is_active,
            applicable_components=list(model.applicable_components or DEFAULT_COMPONENTS),
            applicable_sections=list(getattr(model, "applicable_sections", None) or DEFAULT_SECTIONS),
            created_at=model.created_at,
            updated_at=model.updated_at,
            photos=photos,
            glb_file_name=model.glb_file_name,
            glb_original_name=model.glb_original_name,
            glb_url=glb_url,
        )
