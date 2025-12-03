from enum import Enum


class RoleEnum(str, Enum):
    """
    Enumeración de roles disponibles en la aplicación.
    
    Jerarquía de permisos (de mayor a menor):
    1. SUPERADMIN - Acceso total a la aplicación
    2. ADMIN - Gestión de empresas y usuarios
    3. EMPRESA - Gestión de su propia empresa y datos
    4. USUARIO - Usuario regular con acceso limitado
    """
    SUPERADMIN = "superadmin"
    ADMIN = "admin"
    EMPRESA = "empresa"
    USUARIO = "usuario"


# Mapeo de jerarquía de roles (número mayor = más permisos)
ROLE_HIERARCHY = {
    RoleEnum.SUPERADMIN: 4,
    RoleEnum.ADMIN: 3,
    RoleEnum.EMPRESA: 2,
    RoleEnum.USUARIO: 1,
}


def has_role(user_role: RoleEnum, required_role: RoleEnum) -> bool:
    """
    Verifica si un usuario tiene el rol requerido o superior.
    
    Args:
        user_role: Rol del usuario
        required_role: Rol requerido
        
    Returns:
        True si el usuario tiene el rol requerido o superior
    """
    return ROLE_HIERARCHY.get(user_role, 0) >= ROLE_HIERARCHY.get(required_role, 0)


def has_any_role(user_role: RoleEnum, required_roles: list[RoleEnum]) -> bool:
    """
    Verifica si un usuario tiene alguno de los roles requeridos.
    
    Args:
        user_role: Rol del usuario
        required_roles: Lista de roles permitidos
        
    Returns:
        True si el usuario tiene alguno de los roles requeridos
    """
    return user_role in required_roles
