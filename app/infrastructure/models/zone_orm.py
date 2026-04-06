from datetime import datetime

from sqlalchemy import Column, DateTime, String

from app.infrastructure.database import Base

    #Guarda las zonas únicas extraídas del CSV de ingesta.
class ZoneORM(Base):


    __tablename__ = "zones"

    # Identificador único de la zona — se usa el nombre como PK
    # porque drop_duplicates ya garantiza que son únicos
    name = Column(String, primary_key=True, nullable=False)

    # Fecha en que fue procesada y guardada esta zona
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)