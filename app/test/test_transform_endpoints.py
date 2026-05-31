import os
import sys
import pytest
from unittest.mock import MagicMock, AsyncMock

# Añadir el directorio raíz de este microservicio al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from fastapi.testclient import TestClient
from app.main import app
from app.routers.transform_router import get_transform_service, get_db

# Mock del servicio de transformación
mock_transform_service = MagicMock()

def override_get_transform_service():
    return mock_transform_service

def override_get_db():
    return MagicMock()

@pytest.fixture(autouse=True)
def setup_overrides():
    app.dependency_overrides[get_transform_service] = override_get_transform_service
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.pop(get_transform_service, None)
    app.dependency_overrides.pop(get_db, None)
    mock_transform_service.reset_mock()

def test_health_check():
    client = TestClient(app)
    response = client.get("/api/v1/transform/health")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["status"] == "OK"
    assert data["data"]["service"] == "ms-transform"

def test_test_connection_to_ingestion():
    client = TestClient(app)
    mock_transform_service.test_connection_to_ingestion = AsyncMock(return_value="mocked_ingestion_response")
    
    response = client.post("/api/v1/transform/test-ingestion", json={"texto": "hola"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "✅ Conexión exitosa"
    assert data["respuesta_desde_ingestion"] == "mocked_ingestion_response"
    mock_transform_service.test_connection_to_ingestion.assert_called_once_with("hola")

def test_process_dataset_success():
    client = TestClient(app)
    # TransformMetricsResponse only has: transformed_records, execution_time_ms
    mock_metrics = {
        "transformed_records": 95,
        "execution_time_ms": 150.5
    }
    mock_transform_service.process_dataset = AsyncMock(return_value=mock_metrics)
    
    # Mock send_audit_event in background
    from unittest.mock import patch
    with patch("app.routers.transform_router.send_audit_event", new_callable=AsyncMock) as mock_send_audit:
        response = client.post("/api/v1/transform/dataset_123")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["transformed_records"] == 95
        assert data["data"]["execution_time_ms"] == 150.5
        mock_transform_service.process_dataset.assert_called_once()

def test_process_dataset_value_error():
    client = TestClient(app)
    mock_transform_service.process_dataset = AsyncMock(side_effect=ValueError("Dataset vacío"))
    
    response = client.post("/api/v1/transform/dataset_empty")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert data["error"] == "Dataset vacío"
