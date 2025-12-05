from fastapi import HTTPException, status
from fastapi_users import models
from fastapi_users.manager import BaseUserManager
from app.auth.schemas import LoginRequest
from app.core.security import auth_backend


class AuthService:
    """Servicio para manejar la lógica de autenticación"""
    
    @staticmethod
    async def authenticate_user(
        credentials: LoginRequest,
        user_manager: BaseUserManager[models.UP, models.ID]
    ) -> dict:
        """
        Autentica un usuario con email y contraseña, retornando un token JWT.
        
        Args:
            credentials: Credenciales del usuario (email y password)
            user_manager: Instancia del UserManager
            
        Returns:
            dict: Diccionario con access_token y token_type
            
        Raises:
            HTTPException: Si las credenciales son inválidas o el usuario no está activo
        """
        # Buscar usuario por email
        user = await user_manager.get_by_email(credentials.email)
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="LOGIN_BAD_CREDENTIALS"
            )
        
        # Verificar contraseña
        verified, updated_password_hash = user_manager.password_helper.verify_and_update(
            credentials.password, user.hashed_password
        )
        
        if not verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="LOGIN_BAD_CREDENTIALS"
            )
        
        # Si la contraseña fue actualizada (por ejemplo, rehashed), guardar el nuevo hash
        if updated_password_hash is not None:
            user.hashed_password = updated_password_hash
            await user_manager.user_db.update(user)
        
        # Verificar que el usuario esté activo
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="LOGIN_USER_NOT_VERIFIED"
            )
        
        # Generar token usando la estrategia del backend
        strategy = auth_backend.get_strategy()
        token = await strategy.write_token(user)
        
        return {
            "access_token": token,
            "token_type": "bearer"
        }
