from fastapi import APIRouter
from app.core.security import fastapi_users, auth_backend
from app.users.schemas import UserRead, UserCreate

router = APIRouter()

# Router de autenticación JWT
router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/jwt",
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
