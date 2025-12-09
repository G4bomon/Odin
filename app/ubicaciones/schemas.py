from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class UbicacionBase(BaseModel):
    """Schema base para Ubicacion"""
    ubicacion_id: str = Field(..., max_length=50, description="ID único de la ubicación")
    name: str = Field(..., max_length=100, description="Nombre de la ubicación")
    description: Optional[str] = Field(None, max_length=500, description="Descripción de la ubicación")
    location: Optional[str] = Field(None, max_length=200, description="Ubicación física")
    is_active: bool = Field(True, description="Estado de la ubicación")


class UbicacionCreate(UbicacionBase):
    """Schema para crear una ubicación"""
    pass


class UbicacionUpdate(BaseModel):
    """Schema para actualizar una ubicación"""
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    location: Optional[str] = Field(None, max_length=200)
    is_active: Optional[bool] = None


class UbicacionRead(UbicacionBase):
    """Schema para leer una ubicación"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UbicacionWithStats(UbicacionRead):
    """Schema de ubicación con estadísticas"""
    total_cameras: int = 0
    active_cameras: int = 0
    total_detections: int = 0

    class Config:
        from_attributes = True
