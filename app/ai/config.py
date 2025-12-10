"""
Configuración para el módulo de IA
"""
from pydantic_settings import BaseSettings
from typing import Optional


class AISettings(BaseSettings):
    """
    Configuración para el procesamiento de IA
    """
    # Ruta al modelo de IA
    AI_MODEL_PATH: Optional[str] = "models/yolov8n.pt"
    
    # Intervalo de procesamiento (segundos)
    AI_WORKER_INTERVAL: int = 5
    
    # Habilitar/deshabilitar el worker automático
    AI_WORKER_ENABLED: bool = True
    
    # Confianza mínima para considerar una detección válida
    AI_MIN_CONFIDENCE: float = 0.5
    
    # Clases a detectar (None = todas las clases del modelo)
    AI_DETECTION_CLASSES: Optional[list[str]] = None
    
    # Tamaño de imagen para procesamiento
    AI_IMAGE_SIZE: int = 640
    
    # Usar GPU si está disponible
    AI_USE_GPU: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignorar variables extra del .env


# Instancia global de configuración
ai_settings = AISettings()
