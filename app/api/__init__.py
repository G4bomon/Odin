from fastapi import APIRouter
from app.auth.routes import router as auth_router
from app.users.routes import router as users_router
from app.roles.routes import router as roles_router
from app.locations.routes import router as locations_router
from app.cameras.routes import router as cameras_router
from app.detections.routes import router as detections_router

api_router = APIRouter()

# Incluir routers de dominios
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(roles_router, prefix="/roles", tags=["roles"])
api_router.include_router(locations_router, prefix="/locations", tags=["locations"])
api_router.include_router(cameras_router, prefix="/cameras", tags=["cameras"])
api_router.include_router(detections_router, prefix="/detections", tags=["detections"])