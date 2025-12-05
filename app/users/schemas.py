from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from fastapi_users import schemas
from app.core.roles import RoleEnum


# Schema para leer usuarios (lo que se devuelve en las respuestas)
class UserRead(schemas.BaseUser[int]):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: RoleEnum


# Schema para crear usuarios (lo que el cliente puede enviar)
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Mínimo 8 caracteres")
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    
    class Config:
        extra = "forbid"  # Rechazar cualquier campo adicional


# Schema para actualizar usuarios
class UserUpdate(BaseModel):
    password: Optional[str] = Field(None, min_length=8)
    email: Optional[EmailStr] = None
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    role: Optional[RoleEnum] = Field(None, description="Rol del usuario")
    
    class Config:
        extra = "forbid"
