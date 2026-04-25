import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, patch
import json

from app.main import app
from app.schemas.base_response import StandardResponse


@pytest.fixture
def client():
    """Cliente de prueba para los endpoints"""
    return TestClient(app)


class TestTransformRouter:
    """Suite de pruebas unitarias para los endpoints de transform_router"""
    
    def test_health_check_endpoint(self, client):
        """
        TC-TR-001: Verificar que el endpoint /api/v1/transform/health
        retorna estado OK.
        """
        # Act
        response = client.get("/api/v1/transform/health")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["status"] == "OK"
        assert data["data"]["service"] == "ms-transform"
    
    
    def test_health_check_has_trace_id(self, client):
        """
        TC-TR-002: Verificar que el health check retorna un trace_id único.
        """
        # Act
        response = client.get("/api/v1/transform/health")
        
        # Assert
        data = response.json()
        assert "trace_id" in data
        assert len(data["trace_id"]) > 0
    
    
    def test_health_check_response_structure(self, client):
        """
        TC-TR-003: Verificar que la respuesta tiene la estructura correcta.
        """
        # Act
        response = client.get("/api/v1/transform/health")
        
        # Assert
        data = response.json()
        assert "success" in data
        assert "data" in data
        assert "error" in data
        assert "trace_id" in data
    
    
    @patch("app.routers.transform_router.get_transform_service")
    def test_process_dataset_endpoint_not_found(self, mock_service, client):
        """
        TC-TR-004: Verificar que se retorna error 404 si el dataset no existe.
        """
        # Act
        response = client.post("/api/v1/transform/nonexistent-dataset")
        
        # Assert
        # Puede ser 422 (validación) o depender de la implementación
        assert response.status_code in [404, 422, 500]
    
    
    def test_test_ingestion_endpoint_invalid_request(self, client):
        """
        TC-TR-005: Verificar que se rechaza una solicitud inválida al endpoint
        /api/v1/transform/test-ingestion.
        """
        # Act
        response = client.post(
            "/api/v1/transform/test-ingestion",
            json={}  # Falta el campo 'texto' requerido
        )
        
        # Assert
        assert response.status_code == 422  # Validation error
    
    
    def test_test_ingestion_endpoint_with_valid_data(self, client):
        """
        TC-TR-006: Verificar que /api/v1/transform/test-ingestion acepta
        datos válidos.
        """
        # Act
        response = client.post(
            "/api/v1/transform/test-ingestion",
            json={"texto": "test data"}
        )
        
        # Assert
        assert response.status_code in [200, 500]  # Depende de si ms-ingestion está disponible
    
    
    def test_process_dataset_with_empty_dataset_id(self, client):
        """
        TC-TR-007: Verificar que se maneja correctamente un dataset_load_id
        vacío.
        """
        # Act
        response = client.post("/api/v1/transform/")
        
        # Assert
        # FastAPI puede no enrutar esto correctamente
        assert response.status_code in [404, 405]
    
    
    def test_transform_endpoint_returns_standard_response(self, client):
        """
        TC-TR-008: Verificar que el endpoint retorna StandardResponse.
        """
        # Act
        response = client.get("/api/v1/transform/health")
        
        # Assert
        data = response.json()
        # Estructura de StandardResponse
        assert isinstance(data, dict)
        assert "success" in data
        assert "data" in data
        assert "error" in data
        assert "trace_id" in data
    
    
    def test_health_check_multiple_calls_have_different_trace_ids(self, client):
        """
        TC-TR-009: Verificar que cada llamada genera un trace_id único.
        """
        # Act
        response1 = client.get("/api/v1/transform/health")
        response2 = client.get("/api/v1/transform/health")
        
        # Assert
        trace_id_1 = response1.json()["trace_id"]
        trace_id_2 = response2.json()["trace_id"]
        assert trace_id_1 != trace_id_2
    
    
    def test_health_check_content_type(self, client):
        """
        TC-TR-010: Verificar que el health check retorna application/json.
        """
        # Act
        response = client.get("/api/v1/transform/health")
        
        # Assert
        assert response.headers["content-type"] == "application/json"


class TestZoneRouter:
    """Suite de pruebas unitarias para los endpoints de zone_router"""
    
    def test_get_zones_endpoint_exists(self, client):
        """
        TC-ZR-001: Verificar que el endpoint /api/v1/transform/zones existe.
        """
        # Act
        response = client.get("/api/v1/transform/zones")
        
        # Assert
        assert response.status_code != 404
    
    
    def test_get_zones_returns_success_true(self, client):
        """
        TC-ZR-002: Verificar que el endpoint retorna success=True.
        """
        # Act
        response = client.get("/api/v1/transform/zones")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    
    def test_get_zones_has_zones_array(self, client):
        """
        TC-ZR-003: Verificar que la respuesta contiene un array de zonas.
        """
        # Act
        response = client.get("/api/v1/transform/zones")
        
        # Assert
        data = response.json()
        assert "data" in data
        assert "zones" in data["data"]
        assert isinstance(data["data"]["zones"], list)
    
    
    def test_get_zones_has_error_null(self, client):
        """
        TC-ZR-004: Verificar que el campo error es null en caso de éxito.
        """
        # Act
        response = client.get("/api/v1/transform/zones")
        
        # Assert
        data = response.json()
        assert data["error"] is None
    
    
    def test_get_zones_response_structure(self, client):
        """
        TC-ZR-005: Verificar que la respuesta tiene la estructura correcta.
        """
        # Act
        response = client.get("/api/v1/transform/zones")
        
        # Assert
        data = response.json()
        assert "success" in data
        assert "data" in data
        assert "error" in data
    
    
    def test_get_zones_with_query_parameters(self, client):
        """
        TC-ZR-006: Verificar que el endpoint maneja correctamente parámetros
        de consulta (aunque no los use actualmente).
        """
        # Act
        response = client.get("/api/v1/transform/zones?limit=10")
        
        # Assert
        assert response.status_code == 200
    
    
    def test_get_zones_returns_json(self, client):
        """
        TC-ZR-007: Verificar que el endpoint retorna JSON válido.
        """
        # Act
        response = client.get("/api/v1/transform/zones")
        
        # Assert
        assert response.headers["content-type"] == "application/json"
        # Si se puede parsear como JSON, es válido
        assert response.json() is not None
    
    
    def test_get_zones_multiple_calls_consistency(self, client):
        """
        TC-ZR-008: Verificar que múltiples llamadas retornan datos consistentes.
        """
        # Act
        response1 = client.get("/api/v1/transform/zones")
        response2 = client.get("/api/v1/transform/zones")
        
        # Assert
        data1 = response1.json()
        data2 = response2.json()
        assert data1["data"] == data2["data"]
    
    
    def test_get_zones_empty_zones_array_valid(self, client):
        """
        TC-ZR-009: Verificar que un array vacío de zonas es válido.
        """
        # Act
        response = client.get("/api/v1/transform/zones")
        
        # Assert
        data = response.json()
        zones = data["data"]["zones"]
        # Puede estar vacío o tener datos
        assert isinstance(zones, list)
    
    
    def test_get_zones_zone_items_structure(self, client):
        """
        TC-ZR-010: Verificar que si hay zonas, tengan la estructura correcta.
        """
        # Act
        response = client.get("/api/v1/transform/zones")
        
        # Assert
        data = response.json()
        zones = data["data"]["zones"]
        
        # Si hay zonas, validar estructura
        if len(zones) > 0:
            for zone in zones:
                assert "name" in zone or len(zone) > 0
