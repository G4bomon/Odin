# Re-exportar modelos de dominios para compatibilidad
from app.users.models import User
from app.cameras.models import Camera

__all__=["User","Camera"]