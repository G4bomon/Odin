from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class Camera(Base):
    __tablename__ = "cameras"
    __table_args__ = (
        UniqueConstraint("mac", "deleted_at", name="uq_camera_mac_active"),
        UniqueConstraint("ip", "deleted_at", name="uq_camera_ip_active"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ip: Mapped[str] = mapped_column(String(45), index=True, nullable=False)  # IPv6 safe
    puerto: Mapped[int] = mapped_column(Integer, nullable=False)
    orientacion: Mapped[str] = mapped_column(String(50), nullable=True)
    mac: Mapped[str] = mapped_column(String(50), unique=False, nullable=False, index=True)
    patio_id: Mapped[int] = mapped_column(Integer)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)
    deleted_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=True)
