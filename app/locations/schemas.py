from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class LocationBase(BaseModel):
    """Schema base para Location"""
    location_id: str = Field(..., max_length=50, description="ID único de la ubicación")
    name: str = Field(..., max_length=100, description="Nombre de la ubicación")
    description: Optional[str] = Field(None, max_length=500, description="Descripción de la ubicación")
    address: Optional[str] = Field(None, max_length=200, description="Dirección física")
    is_active: bool = Field(True, description="Estado de la ubicación")


class LocationCreate(LocationBase):
    """Schema para crear una ubicación"""
    pass


class LocationUpdate(BaseModel):
    """Schema para actualizar una ubicación"""
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    address: Optional[str] = Field(None, max_length=200)
    is_active: Optional[bool] = None


class LocationRead(LocationBase):
    """Schema para leer una ubicación"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LocationWithStats(LocationRead):
    """Schema de ubicación con estadísticas"""
    total_cameras: int = 0
    active_cameras: int = 0
    total_detections: int = 0

    class Config:
        from_attributes = True
