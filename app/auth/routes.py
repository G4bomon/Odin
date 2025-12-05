from fastapi import APIRouter, Depends
from app.core.security import fastapi_users, auth_backend
from app.users.schemas import UserRead, UserCreate
from app.auth.schemas import LoginRequest
from app.auth.services import AuthService
from app.users.services import get_user_manager
from fastapi_users import models
from fastapi_users.manager import BaseUserManager

router = APIRouter()

# Endpoint de login con JSON
@router.post("/jwt/login", name="auth:jwt.login")
async def login_json(
    credentials: LoginRequest,
    user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
):
    """
    Endpoint de login que acepta JSON en lugar de FormData.
    
    Envía las credenciales en formato JSON:
    {
        "email": "user@example.com",
        "password": "yourpassword"
    }
    """
    return await AuthService.authenticate_user(credentials, user_manager)

# Router de autenticación JWT original (FormData) - mantener para compatibilidad
router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/jwt/form",
    tags=["auth-formdata"]
)

# Router de registro
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
)

# Router para verificación de email (opcional)
router.include_router(
    fastapi_users.get_verify_router(UserRead),
)

# Router para recuperación de contraseña (opcional)
router.include_router(
    fastapi_users.get_reset_password_router(),
)
