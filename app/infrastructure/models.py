from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.infrastructure.database import Base


class TransformationLog(Base):
    __tablename__ = "transformation_logs"
    # Usamos esto para evitar conflictos si se recarga el módulo
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    dataset_load_id = Column(String, index=True, nullable=False) 
    transformed_records = Column(Integer, nullable=False, default=0)
    execution_time_ms = Column(Float, nullable=False, default=0.0)
    
    # CORRECCIÓN AQUÍ: Solo una vez la palabra datetime
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    zone_analytics = relationship("ZoneAnalytics", back_populates="transformation_log", cascade="all, delete-orphan")


class ZoneAnalytics(Base):
    __tablename__ = "zone_analytics"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    transformation_log_id = Column(Integer, ForeignKey("transformation_logs.id"), nullable=False)
    zone_code = Column(String, index=True, nullable=False)
    zone_name = Column(String, nullable=False)
    region = Column(String, nullable=True) 
    
    # Aquí almacenaremos las numéricas / métricas de manera dinámica
    metrics = Column(JSON, nullable=True)

    # Relaciones
    transformation_log = relationship("TransformationLog", back_populates="zone_analytics")

# NOTA: Eliminé la clase TransformationLogORM porque es REDUNDANTE 
# con TransformationLog. Usa solo una para evitar errores de mapeo.