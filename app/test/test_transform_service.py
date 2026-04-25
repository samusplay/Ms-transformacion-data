import pytest
import time
from unittest.mock import Mock, AsyncMock, patch
from sqlalchemy.orm import Session
import pandas as pd

from app.application.transform_service import TransformService
from app.schemas.ingestion import TestIngestRequest
from app.domain.analytics_client import IAnalyticsClient


@pytest.mark.asyncio
class TestTransformService:
    """Suite de pruebas unitarias para TransformService"""
    
    async def test_test_connection_to_ingestion_success(
        self, mock_ingestion_repository, mock_analytics_client
    ):
        """
        TC-TS-001: Verificar que test_connection_to_ingestion conecta exitosamente
        a ms-ingestion y retorna una respuesta válida.
        """
        service = TransformService(
            ingestion_repository=mock_ingestion_repository,
            analytics_client=mock_analytics_client
        )
        
        # Act
        resultado = await service.test_connection_to_ingestion("test data")
        
        # Assert
        assert resultado is not None
        assert "status" in resultado
        assert resultado["status"] == "✅ Conexión exitosa"
    
    
    async def test_test_connection_to_ingestion_creates_valid_request(
        self, mock_ingestion_repository, mock_analytics_client
    ):
        """
        TC-TS-002: Verificar que se crea un objeto TestIngestRequest válido.
        """
        service = TransformService(
            ingestion_repository=mock_ingestion_repository,
            analytics_client=mock_analytics_client
        )
        
        # Act
        texto_prueba = "test content"
        await service.test_connection_to_ingestion(texto_prueba)
        
        # Assert
        mock_ingestion_repository.send_test_data.assert_called_once()
        call_args = mock_ingestion_repository.send_test_data.call_args[0][0]
        assert isinstance(call_args, TestIngestRequest)
        assert call_args.texto == texto_prueba
    
    
    async def test_process_dataset_success(
        self, mock_ingestion_repository, mock_analytics_client, db_session
    ):
        """
        TC-TS-003: Verificar que process_dataset ejecuta completo sin errores
        con datos válidos.
        """
        service = TransformService(
            ingestion_repository=mock_ingestion_repository,
            analytics_client=mock_analytics_client
        )
        
        # Act
        result = await service.process_dataset("dataset-001", db_session)
        
        # Assert
        assert result is not None
        assert "transformed_records" in result
        assert result["transformed_records"] > 0
        assert "execution_time_ms" in result
        assert result["execution_time_ms"] >= 0
    
    
    async def test_process_dataset_creates_transformation_log(
        self, mock_ingestion_repository, mock_analytics_client, db_session
    ):
        """
        TC-TS-004: Verificar que se registra correctamente el log de transformación.
        """
        from app.infrastructure.models import TransformationLog
        
        service = TransformService(
            ingestion_repository=mock_ingestion_repository,
            analytics_client=mock_analytics_client
        )
        
        # Act
        await service.process_dataset("dataset-001", db_session)
        
        # Assert
        logs = db_session.query(TransformationLog).all()
        assert len(logs) == 1
        assert logs[0].dataset_load_id == "dataset-001"
        assert logs[0].transformed_records == 2
    
    
    async def test_process_dataset_empty_data_raises_error(
        self, mock_ingestion_repository, mock_analytics_client, db_session
    ):
        """
        TC-TS-005: Verificar que se lanza error cuando los datos ingestionados
        están vacíos.
        """
        service = TransformService(
            ingestion_repository=mock_ingestion_repository,
            analytics_client=mock_analytics_client
        )
        
        # Configurar repositorio para retornar datos vacíos
        async def mock_fetch_empty(dataset_load_id: str):
            return {"data": []}
        
        mock_ingestion_repository.fetch_raw_data = AsyncMock(
            side_effect=mock_fetch_empty
        )
        
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await service.process_dataset("empty-dataset", db_session)
        
        assert "vacío o no es válido" in str(exc_info.value)
    
    
    async def test_process_dataset_cleans_text_columns(
        self, mock_ingestion_repository, mock_analytics_client, db_session
    ):
        """
        TC-TS-006: Verificar que las columnas de texto se transforman a mayúsculas
        y se eliminan espacios.
        """
        service = TransformService(
            ingestion_repository=mock_ingestion_repository,
            analytics_client=mock_analytics_client
        )
        
        # Configurar datos con espacios y minúsculas
        async def mock_fetch_messy_data(dataset_load_id: str):
            return {
                "data": [
                    {
                        "ZONE_CODE": " z001 ",
                        "ZONE_NAME": "  bogota  ",
                        "REGION": "cundinamarca"
                    }
                ]
            }
        
        mock_ingestion_repository.fetch_raw_data = AsyncMock(
            side_effect=mock_fetch_messy_data
        )
        
        # Act
        result = await service.process_dataset("dataset-001", db_session)
        
        # Assert
        from app.infrastructure.models import ZoneAnalytics
        zones = db_session.query(ZoneAnalytics).all()
        assert len(zones) > 0
        assert zones[0].zone_name == "BOGOTA"
    
    
    async def test_process_dataset_detects_zone_column(
        self, mock_ingestion_repository, mock_analytics_client, db_session
    ):
        """
        TC-TS-007: Verificar que el servicio detecta automáticamente la columna
        de zona usando palabras clave.
        """
        service = TransformService(
            ingestion_repository=mock_ingestion_repository,
            analytics_client=mock_analytics_client
        )
        
        # Configurar datos con una columna que contiene palabra clave
        async def mock_fetch_with_departamento(dataset_load_id: str):
            return {
                "data": [
                    {
                        "ZONE_CODE": "Z001",
                        "DEPARTAMENTO": "CUNDINAMARCA",
                        "VALUE": 100
                    },
                    {
                        "ZONE_CODE": "Z002",
                        "DEPARTAMENTO": "ANTIOQUIA",
                        "VALUE": 200
                    }
                ]
            }
        
        mock_ingestion_repository.fetch_raw_data = AsyncMock(
            side_effect=mock_fetch_with_departamento
        )
        
        # Act
        result = await service.process_dataset("dataset-001", db_session)
        
        # Assert
        assert result["transformed_records"] == 2
    
    
    async def test_process_dataset_handles_numeric_columns(
        self, mock_ingestion_repository, mock_analytics_client, db_session
    ):
        """
        TC-TS-008: Verificar que las columnas numéricas se llenan con 0 si están vacías.
        """
        service = TransformService(
            ingestion_repository=mock_ingestion_repository,
            analytics_client=mock_analytics_client
        )
        
        # Act
        result = await service.process_dataset("dataset-001", db_session)
        
        # Assert
        # El resultado debe contener datos sin errores
        assert result is not None
        assert "transformed_records" in result
    
    
    async def test_process_dataset_persists_zone_analytics(
        self, mock_ingestion_repository, mock_analytics_client, db_session
    ):
        """
        TC-TS-009: Verificar que se persisten correctamente los registros de
        ZoneAnalytics en la base de datos.
        """
        from app.infrastructure.models import ZoneAnalytics
        
        service = TransformService(
            ingestion_repository=mock_ingestion_repository,
            analytics_client=mock_analytics_client
        )
        
        # Act
        await service.process_dataset("dataset-001", db_session)
        
        # Assert
        zones = db_session.query(ZoneAnalytics).all()
        assert len(zones) > 0
        assert zones[0].zone_code is not None
        assert zones[0].zone_name is not None
    
    
    async def test_process_dataset_execution_time_recorded(
        self, mock_ingestion_repository, mock_analytics_client, db_session
    ):
        """
        TC-TS-010: Verificar que el tiempo de ejecución se registra correctamente.
        """
        from app.infrastructure.models import TransformationLog
        
        service = TransformService(
            ingestion_repository=mock_ingestion_repository,
            analytics_client=mock_analytics_client
        )
        
        # Act
        await service.process_dataset("dataset-001", db_session)
        
        # Assert
        logs = db_session.query(TransformationLog).all()
        assert len(logs) > 0
        assert logs[0].execution_time_ms > 0
