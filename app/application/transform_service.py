import time
from typing import Any, Dict

import pandas as pd
from sqlalchemy.orm import Session

from app.domain.analytics_client import IAnalyticsClient
from app.domain.repository.ingestion_repository import (
    IngestionRepository,
)
from app.infrastructure.models import TransformationLog, ZoneAnalytics
from app.schemas.ingestion import TestIngestRequest


class TransformService:
    """USE CASE: Lógica de negocio de transformación.
    Solo depende del Port (IngestionRepository) → SOLID (DIP)"""

    def __init__(self, ingestion_repository: IngestionRepository, analytics_client: IAnalyticsClient):
        self.ingestion_repository = ingestion_repository
        self.analytics_client = analytics_client

    async def test_connection_to_ingestion(self, texto: str) -> Dict[str, Any]:
        """Prueba de conexión hacia ms-ingestion"""
        request = TestIngestRequest(texto=texto)
        return await self.ingestion_repository.send_test_data(request)

    async def process_dataset(self, dataset_load_id: str, db: Session) -> Dict[str, Any]:
        """Ejecuta el pipeline de transformación completo"""
        start_time = time.time()

        # 1. Obtener datos crudos desde ms-ingestion
        raw_data = await self.ingestion_repository.fetch_raw_data(dataset_load_id)

        records = raw_data.get("data", []) if isinstance(raw_data, dict) else raw_data
        if not records:
            raise ValueError("El dataset provisto por Ingesta está vacío o no es válido.")

        df = pd.DataFrame(records)

        # =========================================================
        # 🧠 CEREBRO: DETECCIÓN AUTOMÁTICA DE ZONA
        # =========================================================
        keywords = ['DEPARTAMENTO', 'ESTADO', 'CIUDAD', 'REGION', 'ZONA', 'PROVINCIA', 'MUNICIPIO']
        col_zona_detectada = None

        for col in df.columns:
            if any(keyword in str(col).upper() for keyword in keywords):
                col_zona_detectada = col
                break

        if not col_zona_detectada:
            cols_texto = df.select_dtypes(include=['object', 'string']).columns
            if len(cols_texto) > 0:
                col_zona_detectada = cols_texto[0]
        # =========================================================

        # 2. Pipeline de limpieza
        text_cols = df.select_dtypes(include=['object', 'string']).columns
        for col in text_cols:
            df[col] = df[col].astype(str).str.strip().str.upper()

        # ── Limpiar números con comas (ej: "4,279" → 4279.0) ──
        for col in df.columns:
            if col not in text_cols:
                continue
            try:
                converted = df[col].str.replace(',', '', regex=False)
                converted = pd.to_numeric(converted, errors='coerce')
                if converted.notna().sum() > len(df) * 0.5:
                    df[col] = converted.fillna(0)
            except Exception:
                pass

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

        # =========================================================
        # 🤖 NUEVO: CÁLCULO DINÁMICO DE MÉTRICAS PARA ML
        # Sin hardcodear nombres de columnas — funciona con cualquier CSV
        # =========================================================
        num_cols_list = df.select_dtypes(include=['number']).columns.tolist()

        if len(num_cols_list) >= 2:
            # poblacion = suma de las últimas columnas numéricas (actividad reciente)
            cols_recientes = num_cols_list[max(0, len(num_cols_list) - 4):]
            df['_poblacion'] = df[cols_recientes].sum(axis=1)

            # ingresos = suma de las primeras columnas numéricas (historial/madurez)
            cols_historicas = num_cols_list[:min(7, len(num_cols_list))]
            df['_ingresos'] = df[cols_historicas].sum(axis=1)
        elif len(num_cols_list) == 1:
            df['_poblacion'] = df[num_cols_list[0]]
            df['_ingresos'] = df[num_cols_list[0]]
        else:
            df['_poblacion'] = 1.0
            df['_ingresos'] = 1.0

        # competencia = cuántos registros comparten la misma zona detectada
        if col_zona_detectada:
            df['_competencia'] = df.groupby(col_zona_detectada)[col_zona_detectada].transform('count').astype(float)
        else:
            df['_competencia'] = 1.0

        # Normalizar las 3 métricas entre 0 y 1 (MinMax dinámico)
        for col in ['_poblacion', '_ingresos', '_competencia']:
            mn, mx = df[col].min(), df[col].max()
            if mx > mn:
                df[col] = (df[col] - mn) / (mx - mn)
            else:
                df[col] = 0.0
        # =========================================================

        # 3. Persistencia en ms-transform
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

            if col_zona_detectada:
                z_name = str(row.get(col_zona_detectada, 'UNKNOWN'))
            else:
                z_name = str(row.get('ZONE_NAME', row.get('zone_name', 'UNKNOWN')))

            region = str(row.get('REGION', row.get('region', 'N/A')))

            handled_keys = {'ZONE_CODE', 'zone_code', 'ZONE_NAME', 'zone_name', 'REGION', 'region',
                            '_poblacion', '_ingresos', '_competencia'}
            if col_zona_detectada:
                handled_keys.add(col_zona_detectada)

            # metrics_dict contiene las columnas originales del CSV
            metrics_dict = {k: v for k, v in row.to_dict().items() if k not in handled_keys}

            # ── Inyectamos las 3 métricas normalizadas para que ms-analytics las use ──
            metrics_dict['poblacion'] = round(float(row['_poblacion']), 4)
            metrics_dict['ingresos'] = round(float(row['_ingresos']), 4)
            metrics_dict['competencia'] = round(float(row['_competencia']), 4)

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

        # 4. Envío a ms-analytics
        cleaned_data_payload = [
            {
                "zone_code": zi.zone_code,
                "zone_name": zi.zone_name,
                "region": zi.region,
                "metrics": zi.metrics
            }
            for zi in zone_instances
        ]

        try:
            await self.analytics_client.send_transformed_data(
                dataset_load_id=dataset_load_id,
                data=cleaned_data_payload
            )
        except Exception as e:
            print(f"Advertencia: No se pudo enviar al pipeline de analítica -> {e}")

        return {
            "transformed_records": transformed_records,
            "zone_column_detected": col_zona_detectada,
            "execution_time_ms": round(execution_time_ms, 2)
        }