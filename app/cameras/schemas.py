from pydantic import field_validator, Field, BaseModel
from typing import Optional
from datetime import datetime
import ipaddress
import re

MAC_RE = re.compile(r"^(?:[0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$|^(?:[0-9A-Fa-f]{2}-){5}[0-9A-Fa-f]{2}$")

class CameraBase(BaseModel):
    ip: str = Field(..., description="Dirección IP de la cámara (IPv4 o IPv6)")
    puerto: int = Field(..., ge=1, le=65535, description="Puerto TCP/UDP")
    orientacion: Optional[str] = Field(None, max_length=50)
    mac: str = Field(..., description="Dirección MAC en formato AA:BB:CC:DD:EE:FF")
    patio_id: Optional[int] = None

    @field_validator("ip")
    def validate_ip(cls, v):
        try:
            ipaddress.ip_address(v)
        except Exception:
            raise ValueError("Dirección IP inválida")
        return v

    @field_validator("mac")
    def validate_mac(cls, v):
        if not MAC_RE.match(v):
            raise ValueError("MAC inválida. Formato esperado: AA:BB:CC:DD:EE:FF (o con guiones)")
        # Normalizar a formato con dos puntos y mayúsculas
        cleaned = v.replace("-", ":").upper()
        return cleaned

    class Config:
        extra = "forbid"


class CameraCreate(CameraBase):
    pass


class CameraUpdate(BaseModel):
    ip: Optional[str] = None
    puerto: Optional[int] = None
    orientacion: Optional[str] = None
    mac: Optional[str] = None
    patio_id: Optional[int] = None

    @field_validator("ip")
    def validate_ip(cls, v):
        if v is None:
            return v
        import ipaddress
        try:
            ipaddress.ip_address(v)
        except Exception:
            raise ValueError("Dirección IP inválida")
        return v

    @field_validator("mac")
    def validate_mac(cls, v):
        if v is None:
            return v
        import re
        MAC_RE = re.compile(r"^(?:[0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$|^(?:[0-9A-Fa-f]{2}-){5}[0-9A-Fa-f]{2}$")
        if not MAC_RE.match(v):
            raise ValueError("MAC inválida. Formato esperado: AA:BB:CC:DD:EE:FF (o con guiones)")
        return v.replace("-", ":").upper()

    class Config:
        extra = "forbid"


class CameraRead(BaseModel):
    id: int
    ip: str
    puerto: int
    orientacion: Optional[str]
    mac: str
    patio_id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    deleted_at: Optional[datetime]

    class Config:
        orm_mode = True
