from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.database import get_async_session
from app.detections.schemas import (
    DetectionCreate,
    DetectionUpdate,
    DetectionRead,
    DetectionFromCamera,
    DetectionResponse,
    DetectionStats,
    DetectionWithDetails,
    DetectionDetailResponse
)
from app.detections.services import DetectionService
from app.core.security import require_empresa
from app.users.models import User
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/upload", response_model=DetectionResponse, status_code=status.HTTP_201_CREATED)
async def upload_detection_from_camera(
    ubicacion_id: str = Form(..., description="ID de la ubicación"),
    mac: str = Form(..., description="MAC address de la cámara"),
    image_path: str = Form(..., description="Ruta de la imagen"),
    image: Optional[UploadFile] = File(None, description="Archivo de imagen (opcional)"),
    db: AsyncSession = Depends(get_async_session)
):
    """
    **Endpoint para recibir detecciones desde la cámara Hikvision o teléfono móvil**
    
    Este endpoint NO requiere autenticación para permitir que las cámaras/móviles envíen datos.
    
    **Formato esperado (multipart/form-data):**
    - ubicacion_id: ID de la ubicación (ej: "ubicacion_001")
    - mac: MAC address de la cámara (ej: "AA:BB:CC:DD:EE:FF")
    - image_path: Ruta de la imagen en el sistema de la cámara
    - image: Archivo de imagen (binario)
    
    **Ejemplo con cURL:**
    ```bash
    curl -X POST "http://localhost:8000/detections/upload" \\
      -F "ubicacion_id=ubicacion_001" \\
      -F "mac=AA:BB:CC:DD:EE:FF" \\
      -F "image_path=/path/to/image.jpg" \\
      -F "image=@image.jpg"
    ```
    
    **Ejemplo desde cámara Hikvision:**
    ```json
    {
      "body": {
        "patio_id": "patio_001",
        "mac": "AA:BB:CC:DD:EE:FF",
        "image_path": "/path/to/image.jpg"
      },
      "files": {
        "image": "binary_image_data"
      }
    }
    ```
    """
    try:
        # Leer imagen si se envió
        image_data = None
        if image:
            image_data = await image.read()
            logger.info(f"Imagen recibida: {image.filename}, tamaño: {len(image_data)} bytes")
        
        # Crear objeto de datos
        detection_data = DetectionFromCamera(
            ubicacion_id=ubicacion_id,
            mac=mac,
            image_path=image_path
        )
        
        # Crear detección
        detection = await DetectionService.create_detection_from_camera(
            db,
            detection_data,
            image_data
        )
        
        logger.info(f"Detección creada: ID={detection.id}, Ubicación={ubicacion_id}, MAC={mac}")
        
        return DetectionResponse(
            success=True,
            message="Detección recibida correctamente",
            detection_id=detection.id
        )
        
    except ValueError as e:
        logger.error(f"Error de validación: {str(e)}")
        return DetectionResponse(
            success=False,
            message="Error al procesar la detección",
            error=str(e)
        )
    except Exception as e:
        logger.error(f"Error inesperado: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al procesar la detección: {str(e)}"
        )


@router.post("/", response_model=DetectionRead, status_code=status.HTTP_201_CREATED)
async def create_detection(
    detection_data: DetectionCreate,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_empresa)
):
    """
    Crear una detección manualmente (EMPRESA+)
    """
    detection = await DetectionService.create_detection(db, detection_data)
    return detection


@router.get("/", response_model=List[DetectionRead])
async def get_all_detections(
    skip: int = 0,
    limit: int = 100,
    ubicacion_id: Optional[int] = None,
    camera_id: Optional[int] = None,
    processed: Optional[bool] = None,
    detection_type: Optional[str] = None,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_empresa)
):
    """
    Obtener todas las detecciones con filtros (EMPRESA+)
    """
    detections = await DetectionService.get_all_detections(
        db, skip, limit, ubicacion_id, camera_id, processed, detection_type
    )
    return detections


@router.get("/stats", response_model=DetectionStats)
async def get_detection_stats(
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_empresa)
):
    """
    Obtener estadísticas generales de detecciones (EMPRESA+)
    """
    stats = await DetectionService.get_detection_stats(db)
    return stats


@router.get("/{detection_id}", response_model=DetectionRead)
async def get_detection(
    detection_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_empresa)
):
    """
    Obtener una detección por ID (EMPRESA+)
    """
    detection = await DetectionService.get_detection(db, detection_id)
    if not detection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Detección {detection_id} no encontrada"
        )
    return detection


@router.get("/{detection_id}/details", response_model=DetectionDetailResponse)
async def get_detection_details(
    detection_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_empresa)
):
    """
    Obtener detección con detalles en formato similar al enviado por la cámara (EMPRESA+)
    
    Retorna la información en el mismo formato que la cámara Hikvision envía,
    facilitando la depuración y verificación de datos.
    """
    detection = await DetectionService.get_detection(db, detection_id)
    if not detection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Detección {detection_id} no encontrada"
        )
    
    # Obtener información de la cámara y ubicación
    from app.cameras.services import CameraService
    from app.ubicaciones.services import UbicacionService
    
    camera = await CameraService.get_camera(db, detection.camera_id)
    ubicacion = await UbicacionService.get_ubicacion(db, detection.ubicacion_id)
    
    # Construir respuesta en formato similar al de la cámara
    return DetectionDetailResponse(
        endpoint="POST /detections/upload",
        body={
            "ubicacion_id": ubicacion.ubicacion_id if ubicacion else None,
            "mac": camera.mac if camera else None,
            "image_path": detection.image_path
        },
        files={
            "image": detection.image_path if detection.image_path else "No image"
        },
        metadata={
            "detection_id": detection.id,
            "ubicacion_name": ubicacion.name if ubicacion else None,
            "camera_name": camera.name if camera else None,
            "camera_model": camera.model if camera else None,
            "camera_orientation": camera.orientacion if camera else None,
            "detection_type": detection.detection_type,
            "objects_detected": detection.objects_detected,
            "created_at": detection.created_at.isoformat(),
            "configuration": {
                "api_url": "tu_puta_api_rul",
                # "api_url": f"{current_user.email.split('@')[0]}_api_url",  # Placeholder, ajustar según settings
                "camera_mac": camera.mac if camera else None,
                "ubicacion_id": ubicacion.ubicacion_id if ubicacion else None,
                "error_log_file": "logs/api_404_errors.jsonl"
            }
        }
    )


@router.patch("/{detection_id}", response_model=DetectionRead)
async def update_detection(
    detection_id: int,
    detection_data: DetectionUpdate,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_empresa)
):
    """
    Actualizar una detección (EMPRESA+)
    
    Útil para actualizar resultados del procesamiento de IA
    """
    detection = await DetectionService.update_detection(db, detection_id, detection_data)
    if not detection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Detección {detection_id} no encontrada"
        )
    return detection


@router.delete("/{detection_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_detection(
    detection_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_empresa)
):
    """
    Eliminar una detección (EMPRESA+)
    """
    deleted = await DetectionService.delete_detection(db, detection_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Detección {detection_id} no encontrada"
        )
    return None
