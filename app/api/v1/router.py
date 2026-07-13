"""API v1 router aggregator."""

from fastapi import APIRouter

from app.api.v1.endpoints import aircraft_models, auth, inspections, photo_annotations

api_v1_router = APIRouter()
api_v1_router.include_router(auth.router)
api_v1_router.include_router(inspections.router)
api_v1_router.include_router(aircraft_models.router)
api_v1_router.include_router(photo_annotations.router)
