from sqlalchemy import String, Boolean, DateTime, Integer, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.database import Base


class Detection(Base):
    """
    Modelo de Detección
    Representa una detección realizada por la IA a partir de una imagen de cámara
    """
    __tablename__ = "detections"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Relaciones con ubicación y cámara
    ubicacion_id: Mapped[int] = mapped_column(Integer, ForeignKey("ubicaciones.id"), nullable=False)
    camera_id: Mapped[int] = mapped_column(Integer, ForeignKey("cameras.id"), nullable=False)
    
    # Información de la imagen
    image_path: Mapped[str] = mapped_column(String(500), nullable=False)
    image_url: Mapped[str] = mapped_column(String(500), nullable=True)  # URL pública si se sube a cloud
    
    # Resultados de la detección
    detection_type: Mapped[str] = mapped_column(String(50), nullable=True)  # threat, face, object, etc.
    confidence: Mapped[float] = mapped_column(nullable=True)  # Confianza de la detección (0-1)
    objects_detected: Mapped[dict] = mapped_column(JSON, nullable=True)  # Lista de objetos detectados
    
    # Metadata adicional
    processed: Mapped[bool] = mapped_column(Boolean, default=False)
    processing_time: Mapped[float] = mapped_column(nullable=True)  # Tiempo de procesamiento en segundos
    error_message: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    processed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # Relaciones
    ubicacion: Mapped["Ubicacion"] = relationship("Ubicacion", back_populates="detections")
    camera: Mapped["Camera"] = relationship("Camera", back_populates="detections")

    def __repr__(self):
        return f"<Detection {self.id}: {self.detection_type} at {self.created_at}>"
