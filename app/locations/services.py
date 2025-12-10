from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from app.locations.models import Location
from app.locations.schemas import LocationCreate, LocationUpdate
from app.cameras.models import Camera
from app.detections.models import Detection


class LocationService:
    """Servicio para gestión de locationes"""

    @staticmethod
    async def create_location(db: AsyncSession, location_data: LocationCreate) -> Location:
        """Crear una nueva ubicación"""
        location = Location(**location_data.model_dump())
        db.add(location)
        await db.commit()
        await db.refresh(location)
        return location

    @staticmethod
    async def get_location(db: AsyncSession, location_id: int) -> Optional[Location]:
        """Obtener una ubicación por ID"""
        result = await db.execute(
            select(Location).where(Location.id == location_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_location_by_location_id(db: AsyncSession, location_id: str) -> Optional[Location]:
        """Obtener una ubicación por location_id (string)"""
        result = await db.execute(
            select(Location).where(Location.location_id == location_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all_locationes(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None
    ) -> List[Location]:
        """Obtener todas las locationes con paginación"""
        query = select(Location)
        
        if is_active is not None:
            query = query.where(Location.is_active == is_active)
        
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def update_location(
        db: AsyncSession,
        location_id: int,
        location_data: LocationUpdate
    ) -> Optional[Location]:
        """Actualizar una ubicación"""
        location = await LocationService.get_location(db, location_id)
        if not location:
            return None

        update_data = location_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(location, field, value)

        await db.commit()
        await db.refresh(location)
        return location

    @staticmethod
    async def delete_location(db: AsyncSession, location_id: int) -> bool:
        """Eliminar una ubicación"""
        location = await LocationService.get_location(db, location_id)
        if not location:
            return False

        await db.delete(location)
        await db.commit()
        return True

    @staticmethod
    async def get_location_with_stats(db: AsyncSession, location_id: int) -> Optional[dict]:
        """Obtener ubicación con estadísticas"""
        location = await LocationService.get_location(db, location_id)
        if not location:
            return None

        # Contar cámaras
        total_cameras_result = await db.execute(
            select(func.count(Camera.id)).where(Camera.location_id == location_id)
        )
        total_cameras = total_cameras_result.scalar() or 0

        active_cameras_result = await db.execute(
            select(func.count(Camera.id)).where(
                Camera.location_id == location_id,
                Camera.is_active == True
            )
        )
        active_cameras = active_cameras_result.scalar() or 0

        # Contar detecciones
        total_detections_result = await db.execute(
            select(func.count(Detection.id)).where(Detection.location_id == location_id)
        )
        total_detections = total_detections_result.scalar() or 0

        return {
            **location.__dict__,
            "total_cameras": total_cameras,
            "active_cameras": active_cameras,
            "total_detections": total_detections
        }
