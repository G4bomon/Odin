from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import api_router
from app.core.security import fastapi_users
from app.users.schemas import UserRead, UserUpdate

app = FastAPI(
    title="Mi API con FastAPI Users",
    description="API con autenticación, roles y permisos",
    version="1.0.0"
)

# Configurar CORS (ajusta según tus necesidades)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica los orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir el router principal de la API
app.include_router(api_router)

# Router de gestión de usuarios (CRUD de usuarios)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)


@app.get("/", tags=["root"])
async def root():
    """
    Endpoint raíz de la API
    """
    return {
        "message": "API funcionando correctamente",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health", tags=["health"])
async def health_check():
    """
    Verificar el estado de la API
    """
    return {"status": "healthy"}