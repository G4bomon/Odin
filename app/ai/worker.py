"""
Worker para procesar detecciones en background
Este worker busca detecciones sin procesar y las procesa con IA
"""
import asyncio
import logging
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_maker
from app.detections.models import Detection
from app.ai.processor import get_ai_processor

logger = logging.getLogger(__name__)


class DetectionWorker:
    """
    Worker que procesa detecciones pendientes en background
    """
    
    def __init__(self, interval_seconds: int = 5, model_path: str = None):
        """
        Args:
            interval_seconds: Intervalo entre cada chequeo (segundos)
            model_path: Ruta al modelo de IA
        """
        self.interval_seconds = interval_seconds
        self.model_path = model_path
        self.is_running = False
        self.ai_processor = get_ai_processor(model_path)
        
    async def process_pending_detections(self, db: AsyncSession):
        """
        Buscar y procesar todas las detecciones pendientes
        """
        try:
            # Buscar detecciones sin procesar
            stmt = select(Detection).where(Detection.processed == False)
            result = await db.execute(stmt)
            pending_detections = result.scalars().all()
            
            if not pending_detections:
                logger.debug("No hay detecciones pendientes")
                return
            
            logger.info(f"Procesando {len(pending_detections)} detecciones pendientes")
            
            for detection in pending_detections:
                await self.process_single_detection(db, detection)
                
        except Exception as e:
            logger.error(f"Error procesando detecciones: {e}")
    
    async def process_single_detection(self, db: AsyncSession, detection: Detection):
        """
        Procesar una sola detección
        """
        try:
            logger.info(f"Procesando detección ID: {detection.id}")
            
            # Procesar imagen con IA
            result = await self.ai_processor.process_image(detection.image_path)
            
            # Actualizar detección con resultados
            detection.processed = result["success"]
            detection.confidence = result["confidence"]
            detection.detection_type = result["detection_type"]
            detection.objects_detected = result["objects_detected"]
            detection.processing_time = result["processing_time"]
            detection.error_message = result["error_message"]
            detection.processed_at = datetime.utcnow()
            
            await db.commit()
            await db.refresh(detection)
            
            logger.info(
                f"Detección {detection.id} procesada: "
                f"type={detection.detection_type}, "
                f"confidence={detection.confidence}, "
                f"time={detection.processing_time}s"
            )
            
        except Exception as e:
            logger.error(f"Error procesando detección {detection.id}: {e}")
            
            # Marcar como procesada con error
            detection.processed = True
            detection.error_message = str(e)
            detection.processed_at = datetime.utcnow()
            await db.commit()
    
    async def run(self):
        """
        Ejecutar el worker en loop infinito
        """
        logger.info(f"Iniciando worker de detecciones (intervalo: {self.interval_seconds}s)")
        self.is_running = True
        
        # Cargar modelo al inicio
        await self.ai_processor.load_model()
        
        while self.is_running:
            try:
                async with async_session_maker() as db:
                    await self.process_pending_detections(db)
                    
            except Exception as e:
                logger.error(f"Error en loop del worker: {e}")
            
            # Esperar antes del siguiente ciclo
            await asyncio.sleep(self.interval_seconds)
    
    def stop(self):
        """
        Detener el worker
        """
        logger.info("Deteniendo worker de detecciones")
        self.is_running = False


# Instancia global del worker
_worker: DetectionWorker = None


def get_worker(interval_seconds: int = 5, model_path: str = None) -> DetectionWorker:
    """
    Obtener instancia del worker (Singleton)
    """
    global _worker
    if _worker is None:
        _worker = DetectionWorker(interval_seconds, model_path)
    return _worker


async def start_worker(interval_seconds: int = 5, model_path: str = None):
    """
    Iniciar el worker en background
    """
    worker = get_worker(interval_seconds, model_path)
    await worker.run()
