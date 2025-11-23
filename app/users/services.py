from typing import Optional
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, IntegerIDMixin
from app.users.models import User
from app.users.schemas import UserCreate
from app.database import get_async_session
from fastapi_users.db import SQLAlchemyUserDatabase
from app.config import settings

# Constantes para tokens
SECRET = settings.SECRET_KEY

class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET
    
    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"Usuario {user.email} se ha registrado.")
    
    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"Usuario {user.email} ha olvidado su contraseña. Token: {token}")
    
    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"Verificación solicitada para {user.email}. Token: {token}")
    
    async def create(
        self,
        user_create: UserCreate,
        safe: bool = False,
        request: Optional[Request] = None,
    ) -> User:
        """
        Sobrescribir el método create para establecer valores por defecto seguros
        """
        # Crear diccionario con los datos del usuario
        user_dict = user_create.model_dump()
        
        # Establecer valores por defecto seguros
        user_dict["is_active"] = True
        user_dict["is_superuser"] = False
        user_dict["is_verified"] = False
        
        # Hashear la contraseña
        password = user_dict.pop("password")
        user_dict["hashed_password"] = self.password_helper.hash(password)
        
        # Crear el usuario en la base de datos
        db_user = User(**user_dict)
        self.user_db.session.add(db_user)
        await self.user_db.session.commit()
        await self.user_db.session.refresh(db_user)
        
        await self.on_after_register(db_user, request)
        
        return db_user


async def get_user_db(session=Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)
