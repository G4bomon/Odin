from fastapi import APIRouter, Depends
from app.models.user import User
from app.core.security import current_active_user, current_superuser
from typing import List

router = APIRouter()


@router.get("/me", response_model=dict)
async def get_current_user(user: User = Depends(current_active_user)):
    """
    Obtener información del usuario actual
    """
    return {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_active": user.is_active,
        "is_superuser": user.is_superuser,
        "is_verified": user.is_verified,
    }


@router.get("/protected-route")
async def protected_route(user: User = Depends(current_active_user)):
    """
    Ruta protegida de ejemplo - requiere autenticación
    """
    return {
        "message": f"Hola {user.email}!",
        "user_id": user.id,
        "full_name": f"{user.first_name} {user.last_name}"
    }


@router.get("/admin-only")
async def admin_only(user: User = Depends(current_superuser)):
    """
    Ruta solo para superusuarios
    """
    return {
        "message": "Solo administradores pueden ver esto",
        "admin_email": user.email
    }


@router.get("/profile")
async def get_profile(user: User = Depends(current_active_user)):
    """
    Obtener perfil completo del usuario
    """
    return {
        "profile": {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_verified": user.is_verified,
        }
    }