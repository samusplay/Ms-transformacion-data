import pytest
from unittest.mock import Mock, AsyncMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import pandas as pd
from typing import Dict, Any, List

from app.infrastructure.models import Base
from app.domain.repository.ingestion_repository import IngestionRepository
from app.domain.repository.zone_repository import ZoneRepository
from app.domain.analytics_client import IAnalyticsClient


@pytest.fixture
def db_session() -> Session:
    """
    Crea una base de datos SQLite en memoria para pruebas.
    Simula la base de datos real sin necesidad de PostgreSQL.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    yield session
    
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def mock_ingestion_repository() -> IngestionRepository:
    """
    Mock para el IngestionRepository.
    Simula las llamadas a ms-ingestion sin necesidad de HTTP real.
    """
    repo = Mock(spec=IngestionRepository)
    
    # Mock de send_test_data
    async def mock_send_test_data(request):
        return {
            "status": "✅ Conexión exitosa",
            "message": "Mock response from ingestion service"
        }
    
    # Mock de fetch_raw_data
    async def mock_fetch_raw_data(dataset_load_id: str):
        return {
            "data": [
                {
                    "ZONE_CODE": "Z001",
                    "ZONE_NAME": "BOGOTA",
                    "REGION": "CUNDINAMARCA",
                    "value": 100
                },
                {
                    "ZONE_CODE": "Z002",
                    "ZONE_NAME": "MEDELLIN",
                    "REGION": "ANTIOQUIA",
                    "value": 200
                }
            ]
        }
    
    repo.send_test_data = AsyncMock(side_effect=mock_send_test_data)
    repo.fetch_raw_data = AsyncMock(side_effect=mock_fetch_raw_data)
    
    return repo


@pytest.fixture
def mock_zone_repository() -> ZoneRepository:
    """
    Mock para el ZoneRepository.
    Simula operaciones de base de datos para zonas.
    """
    repo = Mock(spec=ZoneRepository)
    
    def mock_get_zone_summaries(db):
        return [
            {"name": "BOGOTA", "record_count": 5},
            {"name": "MEDELLIN", "record_count": 3},
            {"name": "CALI", "record_count": 2}
        ]
    
    repo.get_zone_summaries = Mock(side_effect=mock_get_zone_summaries)
    
    return repo


@pytest.fixture
def mock_analytics_client() -> IAnalyticsClient:
    """
    Mock para el cliente de Analytics.
    Simula el envío de datos transformados a ms-analytics.
    """
    client = Mock(spec=IAnalyticsClient)
    
    async def mock_send_transformed_data(dataset_load_id: str, data: List[Dict[str, Any]]) -> bool:
        return True
    
    client.send_transformed_data = AsyncMock(side_effect=mock_send_transformed_data)
    
    return client


@pytest.fixture
def sample_dataset_records() -> List[Dict[str, Any]]:
    """
    Conjunto de datos de prueba que simula registros transformados.
    """
    return [
        {
            "ZONE_CODE": "Z001",
            "ZONE_NAME": "BOGOTA",
            "REGION": "CUNDINAMARCA",
            "population": 8000000,
            "area": 1587
        },
        {
            "ZONE_CODE": "Z002",
            "ZONE_NAME": "MEDELLIN",
            "REGION": "ANTIOQUIA",
            "population": 2500000,
            "area": 380
        },
        {
            "ZONE_CODE": "Z003",
            "ZONE_NAME": "CALI",
            "REGION": "VALLE",
            "population": 2400000,
            "area": 561
        }
    ]


@pytest.fixture
def sample_dataframe() -> pd.DataFrame:
    """
    DataFrame de prueba que simula datos ingestionados.
    """
    return pd.DataFrame([
        {
            "ZONE_CODE": "Z001",
            "ZONE_NAME": "BOGOTA",
            "REGION": "CUNDINAMARCA",
            "value": 100
        },
        {
            "ZONE_CODE": "Z002",
            "ZONE_NAME": "MEDELLIN",
            "REGION": "ANTIOQUIA",
            "value": 200
        }
    ])


@pytest.fixture
def invalid_dataframe_empty_zone() -> pd.DataFrame:
    """
    DataFrame con zone_code vacío para probar validaciones.
    """
    return pd.DataFrame([
        {
            "ZONE_CODE": "",
            "ZONE_NAME": "INVALID",
            "REGION": "TEST"
        }
    ])


@pytest.fixture
def invalid_dataframe_no_zone() -> pd.DataFrame:
    """
    DataFrame sin columna de zona para probar manejo de errores.
    """
    return pd.DataFrame([
        {
            "NAME": "TEST",
            "VALUE": 100
        }
    ])
