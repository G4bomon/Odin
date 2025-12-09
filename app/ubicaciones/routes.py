from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.database import get_async_session
from app.ubicaciones.schemas import UbicacionCreate, UbicacionUpdate, UbicacionRead, UbicacionWithStats
from app.ubicaciones.services import UbicacionService
from app.core.security import require_admin, require_empresa
from app.users.models import User

router = APIRouter()


@router.post("/", response_model=UbicacionRead, status_code=status.HTTP_201_CREATED)
async def create_ubicacion(
    ubicacion_data: UbicacionCreate,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_admin)
):
    """
    Crear una nueva ubicación (Solo ADMIN+)
    """
    # Verificar si ya existe una ubicación con ese ubicacion_id
    existing = await UbicacionService.get_ubicacion_by_ubicacion_id(db, ubicacion_data.ubicacion_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe una ubicación con ID {ubicacion_data.ubicacion_id}"
        )
    
    ubicacion = await UbicacionService.create_ubicacion(db, ubicacion_data)
    return ubicacion


@router.get("/", response_model=List[UbicacionRead])
async def get_all_ubicaciones(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_empresa)
):
    """
    Obtener todas las ubicaciones (EMPRESA+)
    """
    ubicaciones = await UbicacionService.get_all_ubicaciones(db, skip, limit, is_active)
    return ubicaciones


@router.get("/{ubicacion_id}", response_model=UbicacionRead)
async def get_ubicacion(
    ubicacion_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_empresa)
):
    """
    Obtener una ubicación por ID (EMPRESA+)
    """
    ubicacion = await UbicacionService.get_ubicacion(db, ubicacion_id)
    if not ubicacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ubicación {ubicacion_id} no encontrada"
        )
    return ubicacion


@router.get("/{ubicacion_id}/stats", response_model=UbicacionWithStats)
async def get_ubicacion_stats(
    ubicacion_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_empresa)
):
    """
    Obtener ubicación con estadísticas (EMPRESA+)
    """
    ubicacion_stats = await UbicacionService.get_ubicacion_with_stats(db, ubicacion_id)
    if not ubicacion_stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ubicación {ubicacion_id} no encontrada"
        )
    return ubicacion_stats


@router.patch("/{ubicacion_id}", response_model=UbicacionRead)
async def update_ubicacion(
    ubicacion_id: int,
    ubicacion_data: UbicacionUpdate,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_admin)
):
    """
    Actualizar una ubicación (Solo ADMIN+)
    """
    ubicacion = await UbicacionService.update_ubicacion(db, ubicacion_id, ubicacion_data)
    if not ubicacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ubicación {ubicacion_id} no encontrada"
        )
    return ubicacion


@router.delete("/{ubicacion_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ubicacion(
    ubicacion_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_admin)
):
    """
    Eliminar una ubicación (Solo ADMIN+)
    """
    deleted = await UbicacionService.delete_ubicacion(db, ubicacion_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ubicación {ubicacion_id} no encontrada"
        )
    return None
