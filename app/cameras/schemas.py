from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional
import re


class CameraBase(BaseModel):
    """Schema base para Cámara"""
    mac: str = Field(..., max_length=17, description="MAC address de la cámara (AA:BB:CC:DD:EE:FF)")
    name: str = Field(..., max_length=100, description="Nombre de la cámara")
    model: Optional[str] = Field(None, max_length=100, description="Modelo de la cámara")
    ip_address: Optional[str] = Field(None, max_length=15, description="Dirección IP de la cámara")
    orientacion: Optional[str] = Field(None, max_length=100, description="Orientación/ángulo de la cámara (ej: 'Norte', '45° Este', 'Entrada principal')")
    ubicacion_id: int = Field(..., description="ID de la ubicación donde está instalada")
    is_active: bool = Field(True, description="Estado de la cámara")

    @field_validator('mac')
    @classmethod
    def validate_mac(cls, v: str) -> str:
        """Valida formato de MAC address"""
        mac_pattern = r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'
        if not re.match(mac_pattern, v):
            raise ValueError('MAC address debe tener formato AA:BB:CC:DD:EE:FF o AA-BB-CC-DD-EE-FF')
        return v.upper()

    @field_validator('ip_address')
    @classmethod
    def validate_ip(cls, v: Optional[str]) -> Optional[str]:
        """Valida formato de IP address"""
        if v is None:
            return v
        ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if not re.match(ip_pattern, v):
            raise ValueError('IP address debe tener formato XXX.XXX.XXX.XXX')
        # Validar rangos
        parts = v.split('.')
        if not all(0 <= int(part) <= 255 for part in parts):
            raise ValueError('Cada octeto de la IP debe estar entre 0 y 255')
        return v


class CameraCreate(CameraBase):
    """Schema para crear una cámara"""
    pass


class CameraUpdate(BaseModel):
    """Schema para actualizar una cámara"""
    name: Optional[str] = Field(None, max_length=100)
    model: Optional[str] = Field(None, max_length=100)
    ip_address: Optional[str] = Field(None, max_length=15)
    orientacion: Optional[str] = Field(None, max_length=100)
    ubicacion_id: Optional[int] = None
    is_active: Optional[bool] = None

    @field_validator('ip_address')
    @classmethod
    def validate_ip(cls, v: Optional[str]) -> Optional[str]:
        """Valida formato de IP address"""
        if v is None:
            return v
        ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if not re.match(ip_pattern, v):
            raise ValueError('IP address debe tener formato XXX.XXX.XXX.XXX')
        parts = v.split('.')
        if not all(0 <= int(part) <= 255 for part in parts):
            raise ValueError('Cada octeto de la IP debe estar entre 0 y 255')
        return v


class CameraRead(CameraBase):
    """Schema para leer una cámara"""
    id: int
    last_detection: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CameraWithStats(CameraRead):
    """Schema de cámara con estadísticas"""
    total_detections: int = 0
    detections_today: int = 0

    class Config:
        from_attributes = True
