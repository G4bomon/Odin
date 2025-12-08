from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.users.models import User
from app.roles.models import RolePermission
from app.roles.schemas import RolePermissionCreate
from app.core.roles import RoleEnum, ROLE_HIERARCHY


class RoleService:
    """Servicio para gestionar roles y permisos"""
    
    @staticmethod
    async def assign_role(db: AsyncSession, user_id: int, new_role: RoleEnum) -> User:
        """
        Asigna un nuevo rol a un usuario.
        
        Args:
            db: Sesión de base de datos
            user_id: ID del usuario
            new_role: Nuevo rol a asignar
            
        Returns:
            Usuario actualizado
        """
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            return None
        
        user.role = new_role
        await db.commit()
        await db.refresh(user)
        
        return user
    
    @staticmethod
    async def get_users_by_role(db: AsyncSession, role: RoleEnum, skip: int = 0, limit: int = 100) -> list[User]:
        """
        Obtiene todos los usuarios con un rol específico.
        
        Args:
            db: Sesión de base de datos
            role: Rol a filtrar
            skip: Número de registros a omitir
            limit: Límite de registros a devolver
            
        Returns:
            Lista de usuarios con el rol especificado
        """
        stmt = select(User).where(User.role == role).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()
    
    @staticmethod
    async def get_role_info() -> dict:
        """
        Obtiene información sobre todos los roles disponibles.
        
        Returns:
            Diccionario con información de roles
        """
        roles_info = {}
        
        role_descriptions = {
            RoleEnum.SUPERADMIN: "Acceso total a la aplicación. Puede gestionar todo.",
            RoleEnum.ADMIN: "Gestión de empresas y usuarios. Acceso administrativo.",
            RoleEnum.EMPRESA: "Gestión de su propia empresa y datos asociados.",
            RoleEnum.USUARIO: "Usuario regular con acceso limitado a sus propios datos.",
        }
        
        for role, level in ROLE_HIERARCHY.items():
            roles_info[role.value] = {
                "role": role.value,
                "description": role_descriptions.get(role, ""),
                "hierarchy_level": level
            }
        
        return roles_info
    
    @staticmethod
    async def create_permission(db: AsyncSession, permission: RolePermissionCreate) -> RolePermission:
        """
        Crea un nuevo permiso para un rol.
        
        Args:
            db: Sesión de base de datos
            permission: Datos del permiso a crear
            
        Returns:
            Permiso creado
        """
        db_permission = RolePermission(
            role=permission.role.value,
            permission=permission.permission,
            description=permission.description
        )
        db.add(db_permission)
        await db.commit()
        await db.refresh(db_permission)
        
        return db_permission
    
    @staticmethod
    async def get_permissions_by_role(db: AsyncSession, role: RoleEnum) -> list[RolePermission]:
        """
        Obtiene todos los permisos asociados a un rol.
        
        Args:
            db: Sesión de base de datos
            role: Rol a consultar
            
        Returns:
            Lista de permisos del rol
        """
        stmt = select(RolePermission).where(RolePermission.role == role.value)
        result = await db.execute(stmt)
        return result.scalars().all()
