from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.database import get_async_session
from app.locations.schemas import LocationCreate, LocationUpdate, LocationRead, LocationWithStats
from app.locations.services import LocationService
from app.core.security import require_admin, require_empresa
from app.users.models import User

router = APIRouter()


@router.post("/", response_model=LocationRead, status_code=status.HTTP_201_CREATED)
async def create_location(
    location_data: LocationCreate,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_admin)
):
    """
    Crear una nueva ubicación (Solo ADMIN+)
    """
    # Verificar si ya existe una ubicación con ese location_id
    existing = await LocationService.get_location_by_location_id(db, location_data.location_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe una ubicación con ID {location_data.location_id}"
        )
    
    location = await LocationService.create_location(db, location_data)
    return location


@router.get("/", response_model=List[LocationRead])
async def get_all_locationes(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_empresa)
):
    """
    Obtener todas las locationes (EMPRESA+)
    """
    locationes = await LocationService.get_all_locationes(db, skip, limit, is_active)
    return locationes


@router.get("/{location_id}", response_model=LocationRead)
async def get_location(
    location_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_empresa)
):
    """
    Obtener una ubicación por ID (EMPRESA+)
    """
    location = await LocationService.get_location(db, location_id)
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ubicación {location_id} no encontrada"
        )
    return location


@router.get("/{location_id}/stats", response_model=LocationWithStats)
async def get_location_stats(
    location_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_empresa)
):
    """
    Obtener ubicación con estadísticas (EMPRESA+)
    """
    location_stats = await LocationService.get_location_with_stats(db, location_id)
    if not location_stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ubicación {location_id} no encontrada"
        )
    return location_stats


@router.patch("/{location_id}", response_model=LocationRead)
async def update_location(
    location_id: int,
    location_data: LocationUpdate,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_admin)
):
    """
    Actualizar una ubicación (Solo ADMIN+)
    """
    location = await LocationService.update_location(db, location_id, location_data)
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ubicación {location_id} no encontrada"
        )
    return location


@router.delete("/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_location(
    location_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_admin)
):
    """
    Eliminar una ubicación (Solo ADMIN+)
    """
    deleted = await LocationService.delete_location(db, location_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ubicación {location_id} no encontrada"
        )
    return None
