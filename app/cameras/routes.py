from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.database import get_async_session
from app.cameras.schemas import CameraCreate, CameraUpdate, CameraRead, CameraWithStats
from app.cameras.services import CameraService
from app.ubicaciones.services import UbicacionService
from app.core.security import require_admin, require_empresa
from app.users.models import User

router = APIRouter()


@router.post("/", response_model=CameraRead, status_code=status.HTTP_201_CREATED)
async def create_camera(
    camera_data: CameraCreate,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_admin)
):
    """
    Crear una nueva cámara (Solo ADMIN+)
    """
    # Verificar si ya existe una cámara con ese MAC
    existing = await CameraService.get_camera_by_mac(db, camera_data.mac)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe una cámara con MAC {camera_data.mac}"
        )
    
    # Verificar que la ubicación existe
    ubicacion = await UbicacionService.get_ubicacion(db, camera_data.ubicacion_id)
    if not ubicacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ubicación {camera_data.ubicacion_id} no encontrada"
        )
    
    camera = await CameraService.create_camera(db, camera_data)
    return camera


@router.get("/", response_model=List[CameraRead])
async def get_all_cameras(
    skip: int = 0,
    limit: int = 100,
    ubicacion_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_empresa)
):
    """
    Obtener todas las cámaras con filtros (EMPRESA+)
    """
    cameras = await CameraService.get_all_cameras(db, skip, limit, ubicacion_id, is_active)
    return cameras


@router.get("/{camera_id}", response_model=CameraRead)
async def get_camera(
    camera_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_empresa)
):
    """
    Obtener una cámara por ID (EMPRESA+)
    """
    camera = await CameraService.get_camera(db, camera_id)
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cámara {camera_id} no encontrada"
        )
    return camera


@router.get("/mac/{mac}", response_model=CameraRead)
async def get_camera_by_mac(
    mac: str,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_empresa)
):
    """
    Obtener una cámara por MAC address (EMPRESA+)
    """
    camera = await CameraService.get_camera_by_mac(db, mac)
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cámara con MAC {mac} no encontrada"
        )
    return camera


@router.get("/{camera_id}/stats", response_model=CameraWithStats)
async def get_camera_stats(
    camera_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_empresa)
):
    """
    Obtener cámara con estadísticas (EMPRESA+)
    """
    camera_stats = await CameraService.get_camera_with_stats(db, camera_id)
    if not camera_stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cámara {camera_id} no encontrada"
        )
    return camera_stats


@router.patch("/{camera_id}", response_model=CameraRead)
async def update_camera(
    camera_id: int,
    camera_data: CameraUpdate,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_admin)
):
    """
    Actualizar una cámara (Solo ADMIN+)
    """
    # Si se actualiza el ubicacion_id, verificar que existe
    if camera_data.ubicacion_id is not None:
        ubicacion = await UbicacionService.get_ubicacion(db, camera_data.ubicacion_id)
        if not ubicacion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ubicación {camera_data.ubicacion_id} no encontrada"
            )
    
    camera = await CameraService.update_camera(db, camera_id, camera_data)
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cámara {camera_id} no encontrada"
        )
    return camera


@router.delete("/{camera_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_camera(
    camera_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_admin)
):
    """
    Eliminar una cámara (Solo ADMIN+)
    """
    deleted = await CameraService.delete_camera(db, camera_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cámara {camera_id} no encontrada"
        )
    return None
