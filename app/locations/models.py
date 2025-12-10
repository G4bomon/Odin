from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.database import Base


class Location(Base):
    """
    Modelo de Ubicación/Zona de monitoreo
    Representa una ubicación física donde se instalan cámaras
    """
    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    location_id: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    address: Mapped[str] = mapped_column(String(200), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    cameras: Mapped[list["Camera"]] = relationship("Camera", back_populates="location", cascade="all, delete-orphan")
    detections: Mapped[list["Detection"]] = relationship("Detection", back_populates="location", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Location {self.location_id}: {self.name}>"
