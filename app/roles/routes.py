from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_async_session
from app.users.models import User
from app.core.security import require_superadmin, require_admin, current_active_user
from app.core.roles import RoleEnum, ROLE_HIERARCHY
from app.roles.schemas import (
    RolePermissionCreate,
    RolePermissionRead,
    AssignRoleRequest,
    RoleInfo
)
from app.roles.services import RoleService
from app.users.schemas import UserRead

router = APIRouter()


@router.get("/info", response_model=dict)
async def get_roles_info():
    """
    Obtiene información sobre todos los roles disponibles.
    Endpoint público.
    """
    return await RoleService.get_role_info()


@router.get("/hierarchy", response_model=dict)
async def get_roles_hierarchy():
    """
    Obtiene la jerarquía de roles.
    Endpoint público.
    """
    return {
        "hierarchy": {role.value: level for role, level in ROLE_HIERARCHY.items()},
        "description": "Número mayor = más permisos"
    }


@router.post("/assign", response_model=UserRead)
async def assign_role_to_user(
    request: AssignRoleRequest,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_superadmin)
):
    """
    Asigna un rol a un usuario.
    Solo SUPERADMIN puede ejecutar esta acción.
    
    Args:
        request: Contiene user_id y nuevo role
        db: Sesión de base de datos
        current_user: Usuario autenticado (debe ser SUPERADMIN)
    """
    user = await RoleService.assign_role(db, request.user_id, request.role)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    return user


@router.get("/users", response_model=List[UserRead])
async def get_users_by_role(
    role: RoleEnum = Query(..., description="Rol a filtrar"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_admin)
):
    """
    Obtiene todos los usuarios con un rol específico.
    Requiere rol ADMIN o superior.
    """
    users = await RoleService.get_users_by_role(db, role, skip=skip, limit=limit)
    return users


@router.post("/permissions", response_model=RolePermissionRead)
async def create_permission(
    permission: RolePermissionCreate,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_superadmin)
):
    """
    Crea un nuevo permiso para un rol.
    Solo SUPERADMIN puede ejecutar esta acción.
    """
    db_permission = await RoleService.create_permission(db, permission)
    return db_permission


@router.get("/permissions", response_model=List[RolePermissionRead])
async def get_permissions_by_role(
    role: RoleEnum = Query(..., description="Rol a consultar"),
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(current_active_user)
):
    """
    Obtiene todos los permisos asociados a un rol.
    Requiere autenticación.
    """
    permissions = await RoleService.get_permissions_by_role(db, role)
    return permissions


@router.patch("/{user_id}", response_model=UserRead)
async def update_user_role(
    user_id: int,
    request: AssignRoleRequest,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_superadmin)
):
    """
    Actualiza el rol de un usuario.
    Solo SUPERADMIN puede ejecutar esta acción.
    
    Args:
        user_id: ID del usuario a actualizar
        request: Contiene el nuevo role
        db: Sesión de base de datos
        current_user: Usuario autenticado (debe ser SUPERADMIN)
    """
    user = await RoleService.assign_role(db, user_id, request.role)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    return user


@router.get("/my-role", response_model=dict)
async def get_my_role(current_user: User = Depends(current_active_user)):
    """
    Obtiene el rol del usuario autenticado.
    Requiere autenticación.
    """
    return {
        "user_id": current_user.id,
        "email": current_user.email,
        "role": current_user.role.value,
        "hierarchy_level": ROLE_HIERARCHY.get(current_user.role, 0)
    }
