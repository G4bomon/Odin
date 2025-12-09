from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from app.ubicaciones.models import Ubicacion
from app.ubicaciones.schemas import UbicacionCreate, UbicacionUpdate
from app.cameras.models import Camera
from app.detections.models import Detection


class UbicacionService:
    """Servicio para gestión de ubicaciones"""

    @staticmethod
    async def create_ubicacion(db: AsyncSession, ubicacion_data: UbicacionCreate) -> Ubicacion:
        """Crear una nueva ubicación"""
        ubicacion = Ubicacion(**ubicacion_data.model_dump())
        db.add(ubicacion)
        await db.commit()
        await db.refresh(ubicacion)
        return ubicacion

    @staticmethod
    async def get_ubicacion(db: AsyncSession, ubicacion_id: int) -> Optional[Ubicacion]:
        """Obtener una ubicación por ID"""
        result = await db.execute(
            select(Ubicacion).where(Ubicacion.id == ubicacion_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_ubicacion_by_ubicacion_id(db: AsyncSession, ubicacion_id: str) -> Optional[Ubicacion]:
        """Obtener una ubicación por ubicacion_id (string)"""
        result = await db.execute(
            select(Ubicacion).where(Ubicacion.ubicacion_id == ubicacion_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all_ubicaciones(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None
    ) -> List[Ubicacion]:
        """Obtener todas las ubicaciones con paginación"""
        query = select(Ubicacion)
        
        if is_active is not None:
            query = query.where(Ubicacion.is_active == is_active)
        
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def update_ubicacion(
        db: AsyncSession,
        ubicacion_id: int,
        ubicacion_data: UbicacionUpdate
    ) -> Optional[Ubicacion]:
        """Actualizar una ubicación"""
        ubicacion = await UbicacionService.get_ubicacion(db, ubicacion_id)
        if not ubicacion:
            return None

        update_data = ubicacion_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(ubicacion, field, value)

        await db.commit()
        await db.refresh(ubicacion)
        return ubicacion

    @staticmethod
    async def delete_ubicacion(db: AsyncSession, ubicacion_id: int) -> bool:
        """Eliminar una ubicación"""
        ubicacion = await UbicacionService.get_ubicacion(db, ubicacion_id)
        if not ubicacion:
            return False

        await db.delete(ubicacion)
        await db.commit()
        return True

    @staticmethod
    async def get_ubicacion_with_stats(db: AsyncSession, ubicacion_id: int) -> Optional[dict]:
        """Obtener ubicación con estadísticas"""
        ubicacion = await UbicacionService.get_ubicacion(db, ubicacion_id)
        if not ubicacion:
            return None

        # Contar cámaras
        total_cameras_result = await db.execute(
            select(func.count(Camera.id)).where(Camera.ubicacion_id == ubicacion_id)
        )
        total_cameras = total_cameras_result.scalar() or 0

        active_cameras_result = await db.execute(
            select(func.count(Camera.id)).where(
                Camera.ubicacion_id == ubicacion_id,
                Camera.is_active == True
            )
        )
        active_cameras = active_cameras_result.scalar() or 0

        # Contar detecciones
        total_detections_result = await db.execute(
            select(func.count(Detection.id)).where(Detection.ubicacion_id == ubicacion_id)
        )
        total_detections = total_detections_result.scalar() or 0

        return {
            **ubicacion.__dict__,
            "total_cameras": total_cameras,
            "active_cameras": active_cameras,
            "total_detections": total_detections
        }
