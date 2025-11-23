from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.database import get_async_session
from app.products.schemas import ProductCreate, ProductRead, ProductUpdate
from app.products.services import ProductService
from app.core.security import current_active_user
from app.users.models import User

router = APIRouter()


@router.post("/", response_model=ProductRead, status_code=201)
async def create_product(
    product: ProductCreate,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(current_active_user)
):
    """
    Crear un nuevo producto
    Requiere autenticación
    """
    return await ProductService.create_product(db, product)


@router.get("/", response_model=List[ProductRead])
async def get_products(
    skip: int = Query(0, ge=0, description="Número de productos a omitir"),
    limit: int = Query(100, ge=1, le=100, description="Límite de productos a devolver"),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Obtener lista de productos con paginación
    Endpoint público
    """
    return await ProductService.get_products(db, skip=skip, limit=limit)


@router.get("/{product_id}", response_model=ProductRead)
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Obtener un producto por ID
    Endpoint público
    """
    product = await ProductService.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product


@router.put("/{product_id}", response_model=ProductRead)
async def update_product(
    product_id: int,
    product_update: ProductUpdate,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(current_active_user)
):
    """
    Actualizar un producto
    Requiere autenticación
    """
    product = await ProductService.update_product(db, product_id, product_update)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product


@router.delete("/{product_id}", status_code=204)
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(current_active_user)
):
    """
    Eliminar un producto (soft delete)
    Requiere autenticación
    """
    success = await ProductService.delete_product(db, product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Producto no encontrado")


@router.get("/search/{name}", response_model=List[ProductRead])
async def search_products_by_name(
    name: str,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Buscar productos por nombre
    Endpoint público
    """
    # Esta funcionalidad se puede implementar después
    return []