from sqlalchemy import Column, Integer, String, DateTime, JSON, Float, ForeignKey
from sqlalchemy.orm import relationship
import datetime

from app.infrastructure.database import Base

class TransformationLog(Base):
    __tablename__ = "transformation_logs"

    id = Column(Integer, primary_key=True, index=True)
    dataset_load_id = Column(Integer, index=True, nullable=False) # llave foránea lógica a ms-ingestion
    transformed_records = Column(Integer, nullable=False, default=0)
    execution_time_ms = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relaciones
    zone_analytics = relationship("ZoneAnalytics", back_populates="transformation_log", cascade="all, delete-orphan")


class ZoneAnalytics(Base):
    __tablename__ = "zone_analytics"

    id = Column(Integer, primary_key=True, index=True)
    transformation_log_id = Column(Integer, ForeignKey("transformation_logs.id"), nullable=False)
    zone_code = Column(String, index=True, nullable=False)
    zone_name = Column(String, nullable=False)
    region = Column(String, nullable=True) # Otras columnas de texto
    
    # Aquí almacenaremos las numéricas / métricas de manera dinámica
    metrics = Column(JSON, nullable=True)

    # Relaciones
    transformation_log = relationship("TransformationLog", back_populates="zone_analytics")

