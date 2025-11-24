from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Nombre del producto")
    description: Optional[str] = Field(None, description="Descripción del producto")
    price: float = Field(..., gt=0, description="Precio del producto")
    stock: int = Field(0, ge=0, description="Stock disponible")
    is_active: bool = Field(True, description="Producto activo")


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class ProductRead(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True