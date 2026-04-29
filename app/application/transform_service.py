import time
import asyncio
from typing import Any, Dict

import pandas as pd
from sqlalchemy.orm import Session

from app.domain.repository.ingestion_repository import (
    IngestionRepository,  # ← clase pura (Port)
)
from app.domain.repository.audit_client_port import AuditClientPort
from app.infrastructure.models import TransformationLog, ZoneAnalytics
from app.schemas.ingestion import TestIngestRequest  # ← schema correcto


class TransformService:
    """USE CASE: Lógica de negocio de transformación.
    Solo depende del Port (IngestionRepository) → SOLID (DIP)"""

    def __init__(self, ingestion_repository: IngestionRepository, audit_client: AuditClientPort = None):
        """Constructor recibe la interfaz pura (nunca la implementación)"""
        self.ingestion_repository = ingestion_repository
        self.audit_client = audit_client

    async def test_connection_to_ingestion(self, texto: str) -> Dict[str, Any]:
        """Prueba de conexión hacia ms-ingestion"""
        request = TestIngestRequest(texto=texto)
        return await self.ingestion_repository.send_test_data(request)

    async def process_dataset(self, dataset_load_id: str, db: Session, trace_id: str = None) -> Dict[str, Any]:
        """Ejecuta el pipeline de transformación completo"""
        start_time = time.time()
        
        # 1. Hacer petición usando el Repository inyectado (Sólido)
        raw_data = await self.ingestion_repository.fetch_raw_data(dataset_load_id)
        
        # Asegurarnos de que recibimos una lista de records
        records = raw_data.get("data", []) if isinstance(raw_data, dict) else raw_data
        if not records:
            error_msg = "El dataset provisto por Ingesta está vacío o no es válido."
            if self.audit_client and trace_id:
                asyncio.create_task(self.audit_client.send_event("TRANSFORMATION_ERROR", str(dataset_load_id), error_msg, trace_id))
            raise ValueError(error_msg)

        # Convertir a Pandas DataFrame
        df = pd.DataFrame(records)
        
        # =========================================================
        # 🧠 NUEVO CEREBRO: DETECCIÓN AUTOMÁTICA DE ZONA
        # =========================================================
        keywords = ['DEPARTAMENTO', 'ESTADO', 'CIUDAD', 'REGION', 'ZONA', 'PROVINCIA', 'MUNICIPIO']
        col_zona_detectada = None
        
        # 1. Buscamos si el CSV trae alguna columna que haga match con las palabras clave
        for col in df.columns:
            if any(keyword in str(col).upper() for keyword in keywords):
                col_zona_detectada = col
                break
                
        # 2. Si no hay match (CSV muy raro), asumimos la primera columna de texto
        if not col_zona_detectada:
            cols_texto = df.select_dtypes(include=['object', 'string']).columns
            if len(cols_texto) > 0:
                col_zona_detectada = cols_texto[0]
        # =========================================================

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
            error_msg = "El dataset quedó vacío tras el proceso de limpieza de zone_code."
            if self.audit_client and trace_id:
                asyncio.create_task(self.audit_client.send_event("TRANSFORMATION_ERROR", str(dataset_load_id), error_msg, trace_id))
            raise ValueError(error_msg)

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
            
            # 👇 UTILIZAMOS LA COLUMNA DETECTADA POR EL CEREBRO 👇
            if col_zona_detectada:
                z_name = str(row.get(col_zona_detectada, 'UNKNOWN'))
            else:
                z_name = str(row.get('ZONE_NAME', row.get('zone_name', 'UNKNOWN')))
                
            region = str(row.get('REGION', row.get('region', 'N/A')))
            
            # Agregamos la columna detectada a las handled_keys para que no se duplique en metrics
            handled_keys = {'ZONE_CODE', 'zone_code', 'ZONE_NAME', 'zone_name', 'REGION', 'region'}
            if col_zona_detectada:
                handled_keys.add(col_zona_detectada)
                
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

        if self.audit_client and trace_id:
            asyncio.create_task(
                self.audit_client.send_event(
                    event_type="TRANSFORMATION_COMPLETED",
                    reference_id=str(dataset_load_id),
                    summary=f"Finalizó exitosamente el proceso de limpieza y guardado. Registros: {transformed_records}",
                    trace_id=trace_id
                )
            )

        return {
            "transformed_records": transformed_records,
            "zone_column_detected": col_zona_detectada,  # Agregado al return para saber qué columna eligió
            "execution_time_ms": round(execution_time_ms, 2)
        }