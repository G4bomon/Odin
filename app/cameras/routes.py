from fastapi import APIRouter, Depends, Query, Path
from typing import List, Optional
from app.cameras import schemas, services
from app.cameras.models import Camera
from app.core.security import current_active_user, current_superuser
from app.database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/cameras", tags=["cameras"])


@router.get("/", response_model=List[schemas.CameraRead])
async def list_all_cameras(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    include_deleted: bool = Query(False),
    session: AsyncSession = Depends(get_async_session),
    user=Depends(current_active_user),
):
    """
    Listar cámaras. Por defecto sólo cámaras activas (soft-delete respetado).
    """
    cameras = await services.list_cameras(session=session, include_deleted=include_deleted, skip=skip, limit=limit)
    return cameras


@router.get("/{camera_id}", response_model=schemas.CameraRead)
async def get_camera(camera_id: int = Path(..., gt=0), session: AsyncSession = Depends(get_async_session), user=Depends(current_active_user)):
    """
    Obtener cámara por id (incluso si está soft-deleted).
    """
    cam = await services.get_camera(session=session, camera_id=camera_id)
    if not cam:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cámara no encontrada")
    return cam


@router.post("/", response_model=schemas.CameraRead, status_code=201)
async def create_camera(data: schemas.CameraCreate, session: AsyncSession = Depends(get_async_session), user=Depends(current_superuser)):
    """
    Crear cámara. Requiere superusuario (ajústalo si tu política es distinta).
    """
    cam = await services.create_camera(data=data, session=session)
    return cam


@router.put("/{camera_id}", response_model=schemas.CameraRead)
async def update_camera(camera_id: int, data: schemas.CameraUpdate, session: AsyncSession = Depends(get_async_session), user=Depends(current_superuser)):
    """
    Actualizar cámara (partial updates permitidos).
    """
    cam = await services.update_camera(camera_id=camera_id, data=data, session=session)
    return cam


@router.delete("/{camera_id}", response_model=schemas.CameraRead)
async def delete_camera(camera_id: int, session: AsyncSession = Depends(get_async_session), user=Depends(current_superuser)):
    """
    Soft delete de cámara.
    """
    cam = await services.soft_delete_camera(camera_id=camera_id, session=session)
    return cam


@router.post("/{camera_id}/restore", response_model=schemas.CameraRead)
async def restore_camera(camera_id: int, session: AsyncSession = Depends(get_async_session), user=Depends(current_superuser)):
    """
    Restaurar cámara eliminada (soft-undelete).
    """
    cam = await services.restore_camera(camera_id=camera_id, session=session)
    return cam
