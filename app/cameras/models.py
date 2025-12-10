from sqlalchemy import String, Boolean, DateTime, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.database import Base


class Camera(Base):
    """
    Modelo de Cámara Hikvision
    Representa una cámara física instalada en una ubicación
    """
    __tablename__ = "cameras"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    mac: Mapped[str] = mapped_column(String(17), unique=True, index=True, nullable=False)  # AA:BB:CC:DD:EE:FF
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=True)
    ip_address: Mapped[str] = mapped_column(String(15), nullable=True)
    orientacion: Mapped[str] = mapped_column(String(100), nullable=True)  # Ej: "Norte", "45° Este", "Entrada principal"
    location_id: Mapped[int] = mapped_column(Integer, ForeignKey("locations.id"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_detection: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    location: Mapped["Location"] = relationship("Location", back_populates="cameras")
    detections: Mapped[list["Detection"]] = relationship("Detection", back_populates="camera", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Camera {self.mac}: {self.name}>"
