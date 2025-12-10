from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime, timedelta
from typing import List, Optional
from app.cameras.models import Camera
from app.cameras.schemas import CameraCreate, CameraUpdate
from app.detections.models import Detection


class CameraService:
    """Servicio para gestión de cámaras"""

    @staticmethod
    async def create_camera(db: AsyncSession, camera_data: CameraCreate) -> Camera:
        """Crear una nueva cámara"""
        camera = Camera(**camera_data.model_dump())
        db.add(camera)
        await db.commit()
        await db.refresh(camera)
        return camera

    @staticmethod
    async def get_camera(db: AsyncSession, camera_id: int) -> Optional[Camera]:
        """Obtener una cámara por ID"""
        result = await db.execute(
            select(Camera).where(Camera.id == camera_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_camera_by_mac(db: AsyncSession, mac: str) -> Optional[Camera]:
        """Obtener una cámara por MAC address"""
        result = await db.execute(
            select(Camera).where(Camera.mac == mac.upper())
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all_cameras(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        location_id: Optional[int] = None,
        is_active: Optional[bool] = None
    ) -> List[Camera]:
        """Obtener todas las cámaras con filtros"""
        query = select(Camera)
        
        if location_id is not None:
            query = query.where(Camera.location_id == location_id)
        
        if is_active is not None:
            query = query.where(Camera.is_active == is_active)
        
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def update_camera(
        db: AsyncSession,
        camera_id: int,
        camera_data: CameraUpdate
    ) -> Optional[Camera]:
        """Actualizar una cámara"""
        camera = await CameraService.get_camera(db, camera_id)
        if not camera:
            return None

        update_data = camera_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(camera, field, value)

        await db.commit()
        await db.refresh(camera)
        return camera

    @staticmethod
    async def delete_camera(db: AsyncSession, camera_id: int) -> bool:
        """Eliminar una cámara"""
        camera = await CameraService.get_camera(db, camera_id)
        if not camera:
            return False

        await db.delete(camera)
        await db.commit()
        return True

    @staticmethod
    async def update_last_detection(
        db: AsyncSession,
        camera_id: int,
        detection_time: datetime
    ) -> Optional[Camera]:
        """Actualizar timestamp de última detección"""
        camera = await CameraService.get_camera(db, camera_id)
        if not camera:
            return None

        camera.last_detection = detection_time
        await db.commit()
        await db.refresh(camera)
        return camera

    @staticmethod
    async def get_camera_with_stats(db: AsyncSession, camera_id: int) -> Optional[dict]:
        """Obtener cámara con estadísticas"""
        camera = await CameraService.get_camera(db, camera_id)
        if not camera:
            return None

        # Contar detecciones totales
        total_detections_result = await db.execute(
            select(func.count(Detection.id)).where(Detection.camera_id == camera_id)
        )
        total_detections = total_detections_result.scalar() or 0

        # Contar detecciones de hoy
        today = datetime.utcnow().date()
        detections_today_result = await db.execute(
            select(func.count(Detection.id)).where(
                and_(
                    Detection.camera_id == camera_id,
                    func.date(Detection.created_at) == today
                )
            )
        )
        detections_today = detections_today_result.scalar() or 0

        return {
            **camera.__dict__,
            "total_detections": total_detections,
            "detections_today": detections_today
        }
