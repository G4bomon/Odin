from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime, timedelta
from typing import List, Optional
from app.detections.models import Detection
from app.detections.schemas import DetectionCreate, DetectionUpdate, DetectionFromCamera, DetectionStats
from app.cameras.models import Camera
from app.ubicaciones.models import Ubicacion
from app.cameras.services import CameraService
from app.ubicaciones.services import UbicacionService
import os
import uuid
from pathlib import Path


class DetectionService:
    """Servicio para gestión de detecciones"""

    @staticmethod
    async def create_detection(db: AsyncSession, detection_data: DetectionCreate) -> Detection:
        """Crear una nueva detección"""
        detection = Detection(**detection_data.model_dump())
        db.add(detection)
        await db.commit()
        await db.refresh(detection)
        
        # Actualizar timestamp de última detección en la cámara
        await CameraService.update_last_detection(
            db, 
            detection.camera_id, 
            detection.created_at
        )
        
        return detection

    @staticmethod
    async def create_detection_from_camera(
        db: AsyncSession,
        detection_data: DetectionFromCamera,
        image_file: Optional[bytes] = None
    ) -> Optional[Detection]:
        """
        Crear detección desde datos de cámara Hikvision
        Este método maneja la lógica de recepción desde la cámara
        """
        # Buscar ubicación por ubicacion_id
        ubicacion = await UbicacionService.get_ubicacion_by_ubicacion_id(db, detection_data.ubicacion_id)
        if not ubicacion:
            raise ValueError(f"Ubicación {detection_data.ubicacion_id} no encontrada")

        # Buscar cámara por MAC
        camera = await CameraService.get_camera_by_mac(db, detection_data.mac)
        if not camera:
            raise ValueError(f"Cámara con MAC {detection_data.mac} no encontrada")

        # Verificar que la cámara pertenece a la ubicación
        if camera.ubicacion_id != ubicacion.id:
            raise ValueError(
                f"La cámara {detection_data.mac} no pertenece a la ubicación {detection_data.ubicacion_id}"
            )

        # Guardar imagen si se envió
        saved_image_path = detection_data.image_path
        if image_file:
            # Crear directorio si no existe
            upload_dir = Path("uploads/detections")
            upload_dir.mkdir(parents=True, exist_ok=True)
            
            # Generar nombre único para la imagen
            file_extension = ".jpg"  # Por defecto jpg
            if detection_data.image_path:
                file_extension = Path(detection_data.image_path).suffix or ".jpg"
            
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = upload_dir / unique_filename
            
            # Guardar archivo
            with open(file_path, "wb") as f:
                f.write(image_file)
            
            saved_image_path = str(file_path)

        # Crear detección
        detection = Detection(
            ubicacion_id=ubicacion.id,
            camera_id=camera.id,
            image_path=saved_image_path,
            processed=False
        )
        
        db.add(detection)
        await db.commit()
        await db.refresh(detection)
        
        # Actualizar timestamp de última detección en la cámara
        await CameraService.update_last_detection(db, camera.id, detection.created_at)
        
        return detection

    @staticmethod
    async def get_detection(db: AsyncSession, detection_id: int) -> Optional[Detection]:
        """Obtener una detección por ID"""
        result = await db.execute(
            select(Detection).where(Detection.id == detection_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all_detections(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        ubicacion_id: Optional[int] = None,
        camera_id: Optional[int] = None,
        processed: Optional[bool] = None,
        detection_type: Optional[str] = None
    ) -> List[Detection]:
        """Obtener todas las detecciones con filtros"""
        query = select(Detection)
        
        if ubicacion_id is not None:
            query = query.where(Detection.ubicacion_id == ubicacion_id)
        
        if camera_id is not None:
            query = query.where(Detection.camera_id == camera_id)
        
        if detection_type is not None:
            query = query.where(Detection.detection_type == detection_type)
        
        query = query.order_by(Detection.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def update_detection(
        db: AsyncSession,
        detection_id: int,
        detection_data: DetectionUpdate
    ) -> Optional[Detection]:
        """Actualizar una detección"""
        detection = await DetectionService.get_detection(db, detection_id)
        if not detection:
            return None

        update_data = detection_data.model_dump(exclude_unset=True)
        
        # Si se marca como procesada, actualizar timestamp
        if update_data.get('processed') and not detection.processed:
            update_data['processed_at'] = datetime.utcnow()
        
        for field, value in update_data.items():
            setattr(detection, field, value)

        await db.commit()
        await db.refresh(detection)
        return detection

    @staticmethod
    async def delete_detection(db: AsyncSession, detection_id: int) -> bool:
        """Eliminar una detección"""
        detection = await DetectionService.get_detection(db, detection_id)
        if not detection:
            return False

        await db.delete(detection)
        await db.commit()
        return True

    @staticmethod
    async def get_detection_stats(db: AsyncSession) -> DetectionStats:
        """Obtener estadísticas generales de detecciones"""
        # Total de detecciones
        total_result = await db.execute(select(func.count(Detection.id)))
        total_detections = total_result.scalar() or 0

        # Detecciones procesadas
        processed_result = await db.execute(
            select(func.count(Detection.id)).where(Detection.processed == True)
        )
        processed_detections = processed_result.scalar() or 0

        # Detecciones pendientes
        pending_detections = total_detections - processed_detections

        # Detecciones de hoy
        today = datetime.utcnow().date()
        today_result = await db.execute(
            select(func.count(Detection.id)).where(
                func.date(Detection.created_at) == today
            )
        )
        detections_today = today_result.scalar() or 0

        # Detecciones de esta semana
        week_ago = datetime.utcnow() - timedelta(days=7)
        week_result = await db.execute(
            select(func.count(Detection.id)).where(
                Detection.created_at >= week_ago
            )
        )
        detections_this_week = week_result.scalar() or 0

        # Detecciones de este mes
        month_ago = datetime.utcnow() - timedelta(days=30)
        month_result = await db.execute(
            select(func.count(Detection.id)).where(
                Detection.created_at >= month_ago
            )
        )
        detections_this_month = month_result.scalar() or 0

        # Promedio de confianza
        avg_confidence_result = await db.execute(
            select(func.avg(Detection.confidence)).where(
                Detection.confidence.isnot(None)
            )
        )
        average_confidence = avg_confidence_result.scalar()

        # Promedio de tiempo de procesamiento
        avg_time_result = await db.execute(
            select(func.avg(Detection.processing_time)).where(
                Detection.processing_time.isnot(None)
            )
        )
        average_processing_time = avg_time_result.scalar()

        return DetectionStats(
            total_detections=total_detections,
            processed_detections=processed_detections,
            pending_detections=pending_detections,
            detections_today=detections_today,
            detections_this_week=detections_this_week,
            detections_this_month=detections_this_month,
            average_confidence=float(average_confidence) if average_confidence else None,
            average_processing_time=float(average_processing_time) if average_processing_time else None
        )

    @staticmethod
    async def get_detection_with_details(db: AsyncSession, detection_id: int) -> Optional[dict]:
        """Obtener detección con detalles de ubicación y cámara"""
        detection = await DetectionService.get_detection(db, detection_id)
        if not detection:
            return None

        # Obtener ubicación
        ubicacion = await UbicacionService.get_ubicacion(db, detection.ubicacion_id)
        
        # Obtener cámara
        camera = await CameraService.get_camera(db, detection.camera_id)

        return {
            **detection.__dict__,
            "ubicacion_name": ubicacion.name if ubicacion else None,
            "camera_name": camera.name if camera else None,
            "camera_mac": camera.mac if camera else None
        }
