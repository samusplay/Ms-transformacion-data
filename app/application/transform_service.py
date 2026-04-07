# Logica de Negocio (Use Case)
import time
from typing import Any, Dict

import pandas as pd
from sqlalchemy.orm import Session

from app.domain.repository.ingestion_repository import (
    IngestionRepository,  # ← clase pura (Port)
)
from app.infrastructure.models import TransformationLog, ZoneAnalytics
from app.schemas.ingestion import TestIngestRequest  # ← schema correcto


class TransformService:
    """USE CASE: Lógica de negocio de transformación.
    Solo depende del Port (IngestionRepository) → SOLID (DIP)"""

    def __init__(self, ingestion_repository: IngestionRepository):
        """Constructor recibe la interfaz pura (nunca la implementación)"""
        self.ingestion_repository = ingestion_repository

    async def test_connection_to_ingestion(self, texto: str) -> Dict[str, Any]:
        """Prueba de conexión hacia ms-ingestion"""
        request = TestIngestRequest(texto=texto)
        return await self.ingestion_repository.send_test_data(request)

    async def process_dataset(self, dataset_load_id: str, db: Session) -> Dict[str, Any]:
        """Ejecuta el pipeline de transformación completo"""
        start_time = time.time()
        
        # 1. Hacer petición usando el Repository inyectado (Sólido)
        raw_data = await self.ingestion_repository.fetch_raw_data(dataset_load_id)
        
        # Asegurarnos de que recibimos una lista de records
        records = raw_data.get("data", []) if isinstance(raw_data, dict) else raw_data
        if not records:
            raise ValueError("El dataset provisto por Ingesta está vacío o no es válido.")

        # Convertir a Pandas DataFrame
        df = pd.DataFrame(records)
        
        # 2. Pipeline de limpieza en memoria
        text_cols = df.select_dtypes(include=['object', 'string']).columns
        for col in text_cols:
            df[col] = df[col].astype(str).str.strip().str.upper()

        num_cols = df.select_dtypes(include=['number']).columns
        for col in num_cols:
            df[col] = df[col].fillna(0)

        # Tratar zone_code
        if 'ZONE_CODE' in df.columns:
            df = df[df['ZONE_CODE'] != '']
            df = df[df['ZONE_CODE'] != 'NAN']
            df = df.dropna(subset=['ZONE_CODE'])
        elif 'zone_code' in df.columns:
            df = df[df['zone_code'] != '']
            df = df[df['zone_code'] != 'NAN']
            df = df.dropna(subset=['zone_code'])

        if df.empty:
            raise ValueError("El dataset quedó vacío tras el proceso de limpieza de zone_code.")

        # 3. Persistencia 
        execution_time_ms = (time.time() - start_time) * 1000
        transformed_records = len(df)
        
        trans_log = TransformationLog(
            dataset_load_id=dataset_load_id,
            transformed_records=transformed_records,
            execution_time_ms=execution_time_ms
        )
        db.add(trans_log)
        db.commit()
        db.refresh(trans_log)
        
        zone_instances = []
        for _, row in df.iterrows():
            z_code = str(row.get('ZONE_CODE', row.get('zone_code', str(_))))
            z_name = str(row.get('ZONE_NAME', row.get('zone_name', 'UNKNOWN')))
            region = str(row.get('REGION', row.get('region', 'N/A')))
            
            handled_keys = {'ZONE_CODE', 'zone_code', 'ZONE_NAME', 'zone_name', 'REGION', 'region'}
            metrics_dict = {k: v for k, v in row.to_dict().items() if k not in handled_keys}

            zone_analytics = ZoneAnalytics(
                transformation_log_id=trans_log.id,
                zone_code=z_code,
                zone_name=z_name,
                region=region,
                metrics=metrics_dict
            )
            zone_instances.append(zone_analytics)
        
        db.add_all(zone_instances)
        db.commit()

        return {
            "transformed_records": transformed_records,
            "execution_time_ms": round(execution_time_ms, 2)
        }