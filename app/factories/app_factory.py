"""Application factory — centralizes app creation and middleware registration."""

import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.exception_handlers import register_exception_handlers
from app.api.v1.router import api_v1_router
from app.core.config import settings
from app.infrastructure.database.base import Base
from app.infrastructure.database.session import engine
from app.infrastructure.storage.file_storage_service import file_storage_service

logger = logging.getLogger(__name__)


def _initialize_database() -> None:
    try:
        import app.infrastructure.persistence.models.aircraft_model  # noqa: F401
        import app.infrastructure.persistence.models.inspection  # noqa: F401
        import app.infrastructure.persistence.models.organization  # noqa: F401
        import app.infrastructure.persistence.models.user  # noqa: F401

        Base.metadata.create_all(bind=engine)
    except Exception as exc:
        logger.warning("Database initialization skipped: %s", exc)


def create_app() -> FastAPI:
    _initialize_database()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Enterprise API for aircraft physical inspection reports",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)
    app.include_router(api_v1_router)

    upload_path = Path(settings.upload_dir)
    upload_path.mkdir(parents=True, exist_ok=True)
    file_storage_service.ensure_base_dirs()
    app.mount("/uploads", StaticFiles(directory=str(upload_path)), name="uploads")

    @app.get("/api/health", tags=["Health"])
    def health_check() -> dict[str, str]:
        return {"status": "ok"}

    return app
