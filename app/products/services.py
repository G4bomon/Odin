from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from app.products.models import Product
from app.products.schemas import ProductCreate, ProductUpdate


class ProductService:
    
    @staticmethod
    async def create_product(db: AsyncSession, product_data: ProductCreate) -> Product:
        """Crear un nuevo producto"""
        product = Product(**product_data.model_dump())
        db.add(product)
        await db.commit()
        await db.refresh(product)
        return product
    
    @staticmethod
    async def get_product(db: AsyncSession, product_id: int) -> Optional[Product]:
        """Obtener un producto por ID"""
        result = await db.execute(select(Product).where(Product.id == product_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_products(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Product]:
        """Obtener lista de productos con paginación"""
        result = await db.execute(
            select(Product)
            .where(Product.is_active == True)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    @staticmethod
    async def update_product(db: AsyncSession, product_id: int, product_data: ProductUpdate) -> Optional[Product]:
        """Actualizar un producto"""
        product = await ProductService.get_product(db, product_id)
        if not product:
            return None
        
        update_data = product_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(product, field, value)
        
        await db.commit()
        await db.refresh(product)
        return product
    
    @staticmethod
    async def delete_product(db: AsyncSession, product_id: int) -> bool:
        """Eliminar un producto (soft delete)"""
        product = await ProductService.get_product(db, product_id)
        if not product:
            return False
        
        product.is_active = False
        await db.commit()
        return True