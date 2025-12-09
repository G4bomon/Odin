# Re-exportar modelos de dominios para compatibilidad
from app.users.models import User
from app.ubicaciones.models import Ubicacion
from app.cameras.models import Camera
from app.detections.models import Detection

__all__ = ["User", "Ubicacion", "Camera", "Detection"]