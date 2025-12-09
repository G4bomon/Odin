from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any


class DetectionBase(BaseModel):
    """Schema base para Detección"""
    ubicacion_id: int = Field(..., description="ID de la ubicación")
    camera_id: int = Field(..., description="ID de la cámara")
    image_path: str = Field(..., max_length=500, description="Ruta de la imagen")
    detection_type: Optional[str] = Field(None, max_length=50, description="Tipo de detección")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confianza de la detección")
    objects_detected: Optional[Dict[str, Any]] = Field(None, description="Objetos detectados")


class DetectionCreate(DetectionBase):
    """Schema para crear una detección"""
    pass


class DetectionFromCamera(BaseModel):
    """
    Schema para recibir detección desde la cámara Hikvision
    Este es el formato que enviará la cámara
    """
    ubicacion_id: str = Field(..., description="ID de la ubicación (ej: ubicacion_001)")
    mac: str = Field(..., description="MAC address de la cámara")
    image_path: str = Field(..., description="Ruta de la imagen en el sistema de la cámara")


class DetectionUpdate(BaseModel):
    """Schema para actualizar una detección (usado por IA para agregar resultados)"""
    detection_type: Optional[str] = Field(None, max_length=50)
    objects_detected: Optional[Dict[str, Any]] = None


class DetectionRead(BaseModel):
    """Schema para leer una detección (simplificado)"""
    id: int
    ubicacion_id: int
    camera_id: int
    image_path: str
    detection_type: Optional[str] = None
    objects_detected: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class DetectionWithDetails(DetectionRead):
    """Schema de detección con detalles de ubicación y cámara"""
    ubicacion_name: Optional[str] = None
    camera_name: Optional[str] = None
    camera_mac: Optional[str] = None

    class Config:
        from_attributes = True


class DetectionStats(BaseModel):
    """Schema para estadísticas de detecciones"""
    total_detections: int
    processed_detections: int
    pending_detections: int
    detections_today: int
    detections_this_week: int
    detections_this_month: int
    average_confidence: Optional[float] = None
    average_processing_time: Optional[float] = None


class DetectionResponse(BaseModel):
    """Schema de respuesta al recibir una detección"""
    success: bool
    message: str
    detection_id: Optional[int] = None
    error: Optional[str] = None


class DetectionDetailResponse(BaseModel):
    """
    Schema de respuesta para detalles de detección
    Formato similar al que envía la cámara Hikvision
    """
    endpoint: str = Field(..., description="Endpoint usado")
    body: Dict[str, Any] = Field(..., description="Datos del body enviados")
    files: Dict[str, str] = Field(..., description="Información de archivos")
    metadata: Dict[str, Any] = Field(..., description="Metadata adicional")
    
    class Config:
        from_attributes = True
