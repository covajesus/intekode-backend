"""File storage service — handles image persistence on disk (Strategy/Adapter)."""

import shutil
import uuid
from pathlib import Path

from fastapi import UploadFile

from app.core.config import settings
from app.core.exceptions import ApplicationError


class FileStorageService:
    AIRCRAFT_MODELS_DIR = "aircraft-models"

    def __init__(self, base_dir: str | None = None) -> None:
        self._base_dir = Path(base_dir or settings.upload_dir)

    def ensure_base_dirs(self) -> None:
        self._base_dir.mkdir(parents=True, exist_ok=True)
        (self._base_dir / self.AIRCRAFT_MODELS_DIR).mkdir(parents=True, exist_ok=True)

    def _validate_image(self, file: UploadFile) -> str:
        if not file.filename:
            raise ApplicationError("El archivo no tiene nombre")

        extension = file.filename.rsplit(".", 1)[-1].lower()
        if extension not in settings.allowed_image_extensions_list:
            raise ApplicationError(
                f"Formato no permitido. Use: {', '.join(settings.allowed_image_extensions_list)}"
            )
        return extension

    def save_aircraft_model_photo(
        self,
        *,
        model_id: int,
        file: UploadFile,
    ) -> tuple[str, str]:
        self.ensure_base_dirs()
        extension = self._validate_image(file)
        unique_name = f"{uuid.uuid4().hex}.{extension}"
        model_dir = self._base_dir / self.AIRCRAFT_MODELS_DIR / str(model_id)
        model_dir.mkdir(parents=True, exist_ok=True)

        absolute_path = model_dir / unique_name
        with absolute_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        relative_path = f"{self.AIRCRAFT_MODELS_DIR}/{model_id}/{unique_name}"
        return unique_name, relative_path

    def _validate_glb(self, file: UploadFile) -> str:
        if not file.filename:
            raise ApplicationError("El archivo no tiene nombre")

        extension = file.filename.rsplit(".", 1)[-1].lower()
        if extension not in settings.allowed_model3d_extensions_list:
            raise ApplicationError(
                f"Formato 3D no permitido. Use: {', '.join(settings.allowed_model3d_extensions_list)}"
            )
        return extension

    def save_aircraft_model_glb(
        self,
        *,
        model_id: int,
        file: UploadFile,
    ) -> tuple[str, str]:
        self.ensure_base_dirs()
        extension = self._validate_glb(file)
        unique_name = f"model.{extension}"
        model_dir = self._base_dir / self.AIRCRAFT_MODELS_DIR / str(model_id)
        model_dir.mkdir(parents=True, exist_ok=True)

        absolute_path = model_dir / unique_name
        with absolute_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        max_bytes = settings.max_glb_upload_size_mb * 1024 * 1024
        if absolute_path.stat().st_size > max_bytes:
            absolute_path.unlink(missing_ok=True)
            raise ApplicationError(
                f"El modelo 3D supera el tamaño máximo de {settings.max_glb_upload_size_mb} MB"
            )

        relative_path = f"{self.AIRCRAFT_MODELS_DIR}/{model_id}/{unique_name}"
        return unique_name, relative_path

    def delete_file(self, relative_path: str) -> None:
        absolute_path = self._base_dir / relative_path
        if absolute_path.exists() and absolute_path.is_file():
            absolute_path.unlink()

    def delete_model_directory(self, model_id: int) -> None:
        model_dir = self._base_dir / self.AIRCRAFT_MODELS_DIR / str(model_id)
        if model_dir.exists() and model_dir.is_dir():
            shutil.rmtree(model_dir, ignore_errors=True)

    @staticmethod
    def build_public_url(relative_path: str) -> str:
        return f"/uploads/{relative_path.replace(chr(92), '/')}"

    def resolve_absolute_path(self, relative_path: str) -> Path:
        return self._base_dir / relative_path


file_storage_service = FileStorageService()
