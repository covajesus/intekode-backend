"""Public unauthenticated endpoints for shared 3D inspection views."""

from pathlib import Path

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse

from app.api.dependencies import get_public_inspection_service
from app.application.dto.public_inspection import PublicModel3DViewDTO
from app.application.services.public_inspection_service import PublicInspectionService

router = APIRouter(prefix="/api/public/inspections", tags=["Public Inspections"])


@router.get("/{token}/model3d", response_model=PublicModel3DViewDTO)
def get_public_model3d(
    token: str,
    service: PublicInspectionService = Depends(get_public_inspection_service),
) -> PublicModel3DViewDTO:
    return service.get_model3d_view(token)


@router.get("/{token}/model3d/file")
def download_public_model3d_file(
    token: str,
    service: PublicInspectionService = Depends(get_public_inspection_service),
) -> FileResponse:
    path, filename = service.get_glb_file_path(token)
    return FileResponse(
        path=Path(path),
        media_type="model/gltf-binary",
        filename=filename,
    )
