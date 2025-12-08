from fastapi_users.db import SQLAlchemyBaseUserTable
from sqlalchemy import String, Boolean, Enum
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
from app.core.roles import RoleEnum

class User(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(1024), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Campos adicionales personalizados
    first_name: Mapped[str] = mapped_column(String(50), nullable=True)
    last_name: Mapped[str] = mapped_column(String(50), nullable=True)
    
    # Sistema de roles
    role: Mapped[RoleEnum] = mapped_column(
        Enum(RoleEnum, native_enum=False),
        default=RoleEnum.USUARIO,
        nullable=False,
        index=True
    )