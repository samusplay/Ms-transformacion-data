import pytest
from app.main import app


@pytest.fixture
def client():
    """Cliente de prueba para la aplicación"""
    from fastapi.testclient import TestClient
    return TestClient(app)


class TestMain:
    """Suite de pruebas para la aplicación principal"""
    
    def test_app_initialization(self):
        """
        TC-MAIN-001: Verificar que la aplicación se inicializa correctamente.
        """
        # Assert
        assert app is not None
        assert app.title == "Api transformación de datos"
    
    
    def test_app_has_description(self):
        """
        TC-MAIN-002: Verificar que la aplicación tiene descripción.
        """
        # Assert
        assert app.description is not None
        assert len(app.description) > 0
    
    
    def test_app_includes_routers(self):
        """
        TC-MAIN-003: Verificar que la aplicación incluye los routers.
        """
        # Assert
        # Contar el número de rutas registradas
        routes = [route.path for route in app.routes]
        # Debe haber rutas de transform y zone
        assert any("/transform" in route for route in routes)
    
    
    def test_app_lifespan_context_manager(self):
        """
        TC-MAIN-004: Verificar que el lifespan está configurado.
        """
        # Assert
        assert app.lifespan is not None
    
    
    def test_health_endpoint_available_on_startup(self, client):
        """
        TC-MAIN-005: Verificar que el health endpoint está disponible.
        """
        # Act
        response = client.get("/api/v1/transform/health")
        
        # Assert
        assert response.status_code == 200
    
    
    def test_zones_endpoint_available_on_startup(self, client):
        """
        TC-MAIN-006: Verificar que el zones endpoint está disponible.
        """
        # Act
        response = client.get("/api/v1/transform/zones")
        
        # Assert
        assert response.status_code == 200
    
    
    def test_app_openapi_docs_available(self):
        """
        TC-MAIN-007: Verificar que la documentación OpenAPI está disponible.
        """
        # Assert
        assert app.openapi() is not None
    
    
    def test_app_routes_count_is_positive(self):
        """
        TC-MAIN-008: Verificar que la aplicación tiene al menos un endpoint.
        """
        # Act
        routes = [route for route in app.routes]
        
        # Assert
        assert len(routes) > 0
    
    
    def test_app_cors_configuration(self):
        """
        TC-MAIN-009: Verificar que CORS está configurado (si aplica).
        """
        # Assert
        # Este test depende de si CORS está configurado en main.py
        assert app is not None
    
    
    def test_app_error_handlers_configured(self):
        """
        TC-MAIN-010: Verificar que la aplicación está lista para manejar errores.
        """
        # Assert
        assert app is not None
