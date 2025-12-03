from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.core.roles import RoleEnum


class RolePermissionCreate(BaseModel):
    """Schema para crear un permiso de rol"""
    role: RoleEnum
    permission: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class RolePermissionRead(BaseModel):
    """Schema para leer permisos de rol"""
    id: int
    role: RoleEnum
    permission: str
    description: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class AssignRoleRequest(BaseModel):
    """Schema para asignar un rol a un usuario"""
    user_id: int
    role: RoleEnum = Field(..., description="Nuevo rol para el usuario")


class RoleInfo(BaseModel):
    """Schema con información sobre roles disponibles"""
    role: RoleEnum
    description: str
    hierarchy_level: int
