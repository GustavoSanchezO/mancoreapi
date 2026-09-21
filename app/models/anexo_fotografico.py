from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base

class AnexoFotografico(Base):
    __tablename__ = "anexos_fotograficos"

    id = Column(Integer, primary_key=True, index=True)
    cotizacion_id = Column(Integer, ForeignKey("cotizaciones.id", ondelete="CASCADE"), nullable=False)
    ruta_imagen = Column(String(500), nullable=False)

    cotizacion = relationship("CotizacionDB", back_populates="anexos")
