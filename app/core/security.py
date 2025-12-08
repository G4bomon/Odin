from fastapi_users import FastAPIUsers
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi import Depends, HTTPException, status
from app.users.models import User
from app.config import settings
from app.users.services import get_user_manager
from app.core.roles import RoleEnum, has_role, has_any_role

bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=settings.SECRET_KEY, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

# Instancia de FastAPI Users
fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

# Dependencias útiles
current_active_user = fastapi_users.current_user(active=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)


# Dependencias para verificación de roles
async def require_role(required_role: RoleEnum):
    """
    Factory para crear una dependencia que verifica si el usuario tiene el rol requerido o superior.
    
    Uso:
        @router.get("/admin")
        async def admin_endpoint(user: User = Depends(require_role(RoleEnum.ADMIN))):
            ...
    """
    async def role_checker(user: User = Depends(current_active_user)) -> User:
        if not has_role(user.role, required_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Se requiere rol {required_role.value} o superior"
            )
        return user
    return role_checker


async def require_any_role(allowed_roles: list[RoleEnum]):
    """
    Factory para crear una dependencia que verifica si el usuario tiene alguno de los roles permitidos.
    
    Uso:
        @router.get("/content")
        async def content_endpoint(user: User = Depends(require_any_role([RoleEnum.ADMIN, RoleEnum.EMPRESA]))):
            ...
    """
    async def role_checker(user: User = Depends(current_active_user)) -> User:
        if not has_any_role(user.role, allowed_roles):
            roles_str = ", ".join([r.value for r in allowed_roles])
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Se requiere uno de los siguientes roles: {roles_str}"
            )
        return user
    return role_checker


# Dependencias específicas para cada rol
async def require_superadmin(user: User = Depends(current_active_user)) -> User:
    """Requiere rol SUPERADMIN"""
    if not has_role(user.role, RoleEnum.SUPERADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol SUPERADMIN"
        )
    return user


async def require_admin(user: User = Depends(current_active_user)) -> User:
    """Requiere rol ADMIN o superior"""
    if not has_role(user.role, RoleEnum.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol ADMIN o superior"
        )
    return user


async def require_empresa(user: User = Depends(current_active_user)) -> User:
    """Requiere rol EMPRESA o superior"""
    if not has_role(user.role, RoleEnum.EMPRESA):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol EMPRESA o superior"
        )
    return user