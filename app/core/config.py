"""Application configuration — centralized settings (Singleton via pydantic-settings)."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Aviación — Physical Inspection API"
    app_version: str = "1.0.0"
    debug: bool = False

    database_url: str = "mysql+pymysql://root@localhost:3306/aviacion"
    secret_key: str = "dev-secret-key-change-in-production"
    access_token_expire_minutes: int = 480
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    upload_dir: str = "uploads"
    max_upload_size_mb: int = 10
    allowed_image_extensions: str = "jpg,jpeg,png,webp,gif"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def allowed_image_extensions_list(self) -> list[str]:
        return [ext.strip().lower() for ext in self.allowed_image_extensions.split(",") if ext.strip()]


settings = Settings()
