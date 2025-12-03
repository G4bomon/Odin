from fastapi import APIRouter
from app.auth.routes import router as auth_router
from app.users.routes import router as users_router
from app.roles.routes import router as roles_router

api_router = APIRouter()

# Incluir routers de dominios
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(roles_router, prefix="/roles", tags=["roles"])