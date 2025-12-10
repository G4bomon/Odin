"""
Script para resetear la base de datos
CUIDADO: Esto eliminará TODOS los datos

Ejecutar: python reset_db.py
"""
import asyncio
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from app.database import engine
from app.database import Base
from app.users.models import User
from app.locations.models import Location
from app.cameras.models import Camera
from app.detections.models import Detection


async def reset_database():
    """Eliminar todas las tablas y recrearlas"""
    print("\n" + "=" * 60)
    print("⚠️  RESETEO DE BASE DE DATOS")
    print("=" * 60)
    print("\n⚠️  ADVERTENCIA: Esto eliminará TODOS los datos!")
    
    response = input("\n¿Estás seguro? Escribe 'SI' para continuar: ")
    
    if response.upper() != "SI":
        print("\n❌ Operación cancelada.")
        return
    
    print("\n🗑️  Eliminando todas las tablas...")
    
    async with engine.begin() as conn:
        # Eliminar todas las tablas
        await conn.run_sync(Base.metadata.drop_all)
        print("✅ Tablas eliminadas")
        
        # Recrear todas las tablas
        await conn.run_sync(Base.metadata.create_all)
        print("✅ Tablas recreadas")
    
    print("\n✅ Base de datos reseteada exitosamente!")
    print("\n💡 Ahora puedes ejecutar: python seeds.py")


if __name__ == "__main__":
    asyncio.run(reset_database())
