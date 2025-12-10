from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api import api_router
from app.core.security import fastapi_users
from app.users.schemas import UserRead, UserUpdate
import os
import asyncio
from contextlib import asynccontextmanager

# Importar configuración y worker de IA
from app.ai.config import ai_settings
from app.ai.worker import get_worker


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle events: startup y shutdown
    """
    # Startup: Iniciar worker de IA si está habilitado
    worker_task = None
    if ai_settings.AI_WORKER_ENABLED:
        print(f" Iniciando worker de IA (intervalo: {ai_settings.AI_WORKER_INTERVAL}s)")
        worker = get_worker(
            interval_seconds=ai_settings.AI_WORKER_INTERVAL,
            model_path=ai_settings.AI_MODEL_PATH
        )
        worker_task = asyncio.create_task(worker.run())
    
    yield
    
    # Shutdown: Detener worker
    if worker_task:
        print(" Deteniendo worker de IA")
        worker = get_worker()
        worker.stop()
        worker_task.cancel()
        try:
            await worker_task
        except asyncio.CancelledError:
            pass


app = FastAPI(
    title="Mi API con FastAPI Users",
    description="API con autenticación, roles y permisos",
    version="1.0.0",
    lifespan=lifespan
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
    return {
        "status": "healthy",
        "data":""
    
    
    }


@app.get("/mobile", tags=["mobile"])
async def serve_mobile_app():
    """
    Servir la aplicación móvil de prueba
    """
    file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "mobile_test_app.html")
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"error": "Mobile app not found"}