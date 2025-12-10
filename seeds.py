"""
Seeder para poblar la base de datos con datos iniciales
Ejecutar: python seeds.py
"""
import asyncio
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.ext.asyncio import AsyncSession
from app.database import async_session_maker, engine, get_async_session, Base
from app.core.roles import RoleEnum
from app.users.services import get_user_manager, get_user_db
from fastapi_users.password import PasswordHelper

# Importar TODOS los modelos en el orden correcto para resolver relaciones
from app.users.models import User
from app.locations.models import Location
from app.cameras.models import Camera
from app.detections.models import Detection

# Usar el mismo password helper que FastAPI Users
password_helper = PasswordHelper()


def get_password_hash(password: str) -> str:
    """Hashear password usando el mismo sistema que FastAPI Users"""
    return password_helper.hash(password)


async def create_if_not_exists(db: AsyncSession, model, filter_field: str, filter_value, data: dict):
    """
    Función helper: Busca si el registro existe.
    - Si existe: No hace nada
    - Si no existe: Lo crea
    """
    from sqlalchemy import select
    
    # Buscar si existe
    stmt = select(model).where(getattr(model, filter_field) == filter_value)
    result = await db.execute(stmt)
    exists = result.scalar_one_or_none()
    
    if exists:
        print(f"⚠️  {model.__name__} ya existe: {filter_field}={filter_value}")
        return exists
    else:
        # Crear nuevo registro
        new_record = model(**data)
        db.add(new_record)
        await db.commit()
        await db.refresh(new_record)
        print(f"✅ {model.__name__} creado: {filter_field}={filter_value}")
        return new_record


async def seed_data():
    """Función principal de seeding"""
    async with async_session_maker() as db:
        try:
            print("🌱 Iniciando el sembrado de datos (Seeding)...\n")

            # ========================================
            # 1. USUARIOS CON ROLES
            # ========================================
            print("👤 Creando usuarios...")
            
            # Usuario SUPERADMIN
            superadmin = await create_if_not_exists(
                db, User,
                filter_field="email",
                filter_value="superadmin@odin.com",
                data={
                    "email": "superadmin@odin.com",
                    "hashed_password": get_password_hash("super123"),
                    "role": RoleEnum.SUPERADMIN,
                    "first_name": "Super Admin",
                    "is_active": True,
                    "is_superuser": True,
                    "is_verified": True
                }
            )

            # Usuario ADMIN
            admin = await create_if_not_exists(
                db, User,
                filter_field="email",
                filter_value="admin@odin.com",
                data={
                    "email": "admin@odin.com",
                    "hashed_password": get_password_hash("admin123"),
                    "role": RoleEnum.ADMIN,
                    "first_name": "Admin",
                    "is_active": True,
                    "is_superuser": False,
                    "is_verified": True
                }
            )

            # Usuario EMPRESA
            empresa = await create_if_not_exists(
                db, User,
                filter_field="email",
                filter_value="empresa@odin.com",
                data={
                    "email": "empresa@odin.com",
                    "hashed_password": get_password_hash("empresa123"),
                    "role": RoleEnum.EMPRESA,
                    "first_name":"empresa",
                    "is_active": True,
                    "is_superuser": False,
                    "is_verified": True
                }
            )

            # Usuario DEVELOPER (para tu equipo)
            dev = await create_if_not_exists(
                db, User,
                filter_field="email",
                filter_value="dev@odin.com",
                data={
                    "email": "dev@odin.com",
                    "hashed_password": get_password_hash("dev123"),
                    "role": RoleEnum.EMPRESA,
                    "first_name":"dev",
                    "is_active": True,
                    "is_superuser": False,
                    "is_verified": True
                }
            )

            print()

            # ========================================
            # 2. LOCATIONS (UBICACIONES)
            # ========================================
            print("📍 Creando ubicaciones...")
            
            locations_data = [
                {
                    "location_id": "location_001",
                    "name": "Patio Principal",
                    "description": "Área de entrada principal del edificio",
                    "address": "Calle Principal #123, Entrada Norte",
                    "is_active": True
                },
                {
                    "location_id": "location_002",
                    "name": "Almacén General",
                    "description": "Zona de almacenamiento y carga",
                    "address": "Zona de Carga, Edificio B",
                    "is_active": True
                },
                {
                    "location_id": "location_003",
                    "name": "Oficinas Centrales",
                    "description": "Área administrativa principal",
                    "address": "Piso 2, Torre A",
                    "is_active": True
                },
                {
                    "location_id": "location_004",
                    "name": "Estacionamiento",
                    "description": "Zona de estacionamiento vehicular",
                    "address": "Sótano 1",
                    "is_active": True
                },
                {
                    "location_id": "mi_casa",
                    "name": "Mi Casa",
                    "description": "Ubicación de prueba para desarrollo",
                    "address": "Casa de prueba",
                    "is_active": True
                }
            ]

            created_locations = {}
            for loc_data in locations_data:
                location = await create_if_not_exists(
                    db, Location,
                    filter_field="location_id",
                    filter_value=loc_data["location_id"],
                    data=loc_data
                )
                created_locations[loc_data["location_id"]] = location

            print()

            # ========================================
            # 3. CAMERAS (CÁMARAS)
            # ========================================
            print("📷 Creando cámaras...")
            
            cameras_data = [
                {
                    "mac": "AA:BB:CC:DD:EE:01",
                    "name": "Cámara Entrada Principal",
                    "model": "Hikvision DS-2CD2143G0-I",
                    "ip_address": "192.168.1.101",
                    "orientacion": "Frontal - Entrada Norte",
                    "location_id": created_locations["location_001"].id,
                    "is_active": True
                },
                {
                    "mac": "AA:BB:CC:DD:EE:02",
                    "name": "Cámara Almacén 1",
                    "model": "Hikvision DS-2CD2143G0-I",
                    "ip_address": "192.168.1.102",
                    "orientacion": "Lateral - Zona de Carga",
                    "location_id": created_locations["location_002"].id,
                    "is_active": True
                },
                {
                    "mac": "AA:BB:CC:DD:EE:03",
                    "name": "Cámara Oficinas",
                    "model": "Hikvision DS-2CD2143G0-I",
                    "ip_address": "192.168.1.103",
                    "orientacion": "Cenital - Pasillo Principal",
                    "location_id": created_locations["location_003"].id,
                    "is_active": True
                },
                {
                    "mac": "AA:BB:CC:DD:EE:04",
                    "name": "Cámara Estacionamiento",
                    "model": "Hikvision DS-2CD2143G0-I",
                    "ip_address": "192.168.1.104",
                    "orientacion": "Panorámica - Vista General",
                    "location_id": created_locations["location_004"].id,
                    "is_active": True
                },
                {
                    "mac": "AA:BB:CC:DD:EE:05",
                    "name": "Teléfono Móvil",
                    "model": "Smartphone",
                    "ip_address": None,
                    "orientacion": "Frontal",
                    "location_id": created_locations["mi_casa"].id,
                    "is_active": True
                }
            ]

            for cam_data in cameras_data:
                await create_if_not_exists(
                    db, Camera,
                    filter_field="mac",
                    filter_value=cam_data["mac"],
                    data=cam_data
                )

            print()
            print("=" * 60)
            print("🌳 Sembrado completado exitosamente!")
            print("=" * 60)
            print("\n📋 CREDENCIALES DE ACCESO:\n")
            print("SUPERADMIN:")
            print("  Email: superadmin@odin.com")
            print("  Password: super123")
            print()
            print("ADMIN:")
            print("  Email: admin@odin.com")
            print("  Password: admin123")
            print()
            print("EMPRESA:")
            print("  Email: empresa@odin.com")
            print("  Password: empresa123")
            print()
            print("DEVELOPER:")
            print("  Email: dev@odin.com")
            print("  Password: dev123")
            print()
            print("=" * 60)

        except Exception as e:
            print(f"\n❌ Error durante el seeding: {e}")
            import traceback
            traceback.print_exc()
            await db.rollback()
            raise


async def main():
    """Punto de entrada principal"""
    print("\n" + "=" * 60)
    print("🌱 ODIN - Database Seeder")
    print("=" * 60 + "\n")
    
    await seed_data()


if __name__ == "__main__":
    asyncio.run(main())
