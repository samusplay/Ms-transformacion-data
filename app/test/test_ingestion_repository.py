import pytest
import httpx
from unittest.mock import AsyncMock, patch, Mock
from dotenv import load_dotenv

from app.infrastructure.repositories.ingestion_repository_impl import (
    IngestionRepositoryImpl,
)
from app.schemas.ingestion import TestIngestRequest


class TestIngestionRepositoryImpl:
    """Suite de pruebas unitarias para IngestionRepositoryImpl"""
    
    @pytest.fixture
    def repo(self):
        """Instancia del repositorio para pruebas"""
        with patch.dict("os.environ", {"INGESTION_SERVICE_URL": "http://localhost:8001"}):
            return IngestionRepositoryImpl()
    
    
    @pytest.mark.asyncio
    async def test_send_test_data_success(self, repo):
        """
        TC-IR-001: Verificar que send_test_data realiza llamada HTTP exitosa
        a ms-ingestion.
        """
        request = TestIngestRequest(texto="test data")
        
        # Mock de httpx.AsyncClient
        with patch("app.infrastructure.repositories.ingestion_repository_impl.httpx.AsyncClient") as mock_client:
            mock_response = Mock()
            mock_response.json.return_value = {
                "status": "✅ Conexión exitosa",
                "message": "Test successful"
            }
            
            mock_client_instance = AsyncMock()
            mock_client_instance.__aenter__.return_value = mock_client_instance
            mock_client_instance.post = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_client_instance
            
            # Act
            result = await repo.send_test_data(request)
            
            # Assert
            assert result is not None
            assert result["status"] == "✅ Conexión exitosa"
    
    
    @pytest.mark.asyncio
    async def test_send_test_data_correct_url(self, repo):
        """
        TC-IR-002: Verificar que se construye la URL correcta para send_test_data.
        """
        request = TestIngestRequest(texto="test")
        
        with patch("app.infrastructure.repositories.ingestion_repository_impl.httpx.AsyncClient") as mock_client:
            mock_response = Mock()
            mock_response.json.return_value = {"status": "ok"}
            
            mock_client_instance = AsyncMock()
            mock_client_instance.__aenter__.return_value = mock_client_instance
            mock_client_instance.post = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_client_instance
            
            # Act
            await repo.send_test_data(request)
            
            # Assert
            called_url = mock_client_instance.post.call_args[0][0]
            assert "/test-hexagonal" in called_url
    
    
    @pytest.mark.asyncio
    async def test_send_test_data_sends_request_body(self, repo):
        """
        TC-IR-003: Verificar que se envía correctamente el cuerpo de la solicitud.
        """
        request = TestIngestRequest(texto="test content")
        
        with patch("app.infrastructure.repositories.ingestion_repository_impl.httpx.AsyncClient") as mock_client:
            mock_response = Mock()
            mock_response.json.return_value = {"status": "ok"}
            
            mock_client_instance = AsyncMock()
            mock_client_instance.__aenter__.return_value = mock_client_instance
            mock_client_instance.post = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_client_instance
            
            # Act
            await repo.send_test_data(request)
            
            # Assert
            call_kwargs = mock_client_instance.post.call_args[1]
            assert "json" in call_kwargs
            assert call_kwargs["json"]["texto"] == "test content"
    
    
    @pytest.mark.asyncio
    async def test_fetch_raw_data_success(self, repo):
        """
        TC-IR-004: Verificar que fetch_raw_data obtiene datos correctamente.
        """
        with patch("app.infrastructure.repositories.ingestion_repository_impl.httpx.AsyncClient") as mock_client:
            mock_response = Mock()
            mock_response.json.return_value = {
                "data": [
                    {"ZONE_CODE": "Z001", "ZONE_NAME": "BOGOTA"}
                ]
            }
            
            mock_client_instance = AsyncMock()
            mock_client_instance.__aenter__.return_value = mock_client_instance
            mock_client_instance.get = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_client_instance
            
            # Act
            result = await repo.fetch_raw_data("dataset-001")
            
            # Assert
            assert result is not None
            assert "data" in result
            assert len(result["data"]) > 0
    
    
    @pytest.mark.asyncio
    async def test_fetch_raw_data_correct_url(self, repo):
        """
        TC-IR-005: Verificar que se construye la URL correcta para fetch_raw_data.
        """
        dataset_id = "dataset-001"
        
        with patch("app.infrastructure.repositories.ingestion_repository_impl.httpx.AsyncClient") as mock_client:
            mock_response = Mock()
            mock_response.json.return_value = {"data": []}
            
            mock_client_instance = AsyncMock()
            mock_client_instance.__aenter__.return_value = mock_client_instance
            mock_client_instance.get = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_client_instance
            
            # Act
            await repo.fetch_raw_data(dataset_id)
            
            # Assert
            called_url = mock_client_instance.get.call_args[0][0]
            assert dataset_id in called_url
            assert "/raw" in called_url
    
    
    def test_initialization_with_missing_env_var(self):
        """
        TC-IR-006: Verificar que se lanza error si INGESTION_SERVICE_URL no está
        configurada.
        """
        with patch.dict("os.environ", {}, clear=True):
            # Act & Assert
            with pytest.raises(ValueError) as exc_info:
                IngestionRepositoryImpl()
            
            assert "INGESTION_SERVICE_URL" in str(exc_info.value)
    
    
    def test_initialization_with_valid_env_var(self):
        """
        TC-IR-007: Verificar que se inicializa correctamente con URL válida.
        """
        with patch.dict("os.environ", {"INGESTION_SERVICE_URL": "http://localhost:8001"}):
            # Act
            repo = IngestionRepositoryImpl()
            
            # Assert
            assert repo.base_url == "http://localhost:8001"
    
    
    def test_initialization_strips_trailing_slash(self):
        """
        TC-IR-008: Verificar que se eliminan las barras al final de la URL.
        """
        with patch.dict("os.environ", {"INGESTION_SERVICE_URL": "http://localhost:8001/"}):
            # Act
            repo = IngestionRepositoryImpl()
            
            # Assert
            assert repo.base_url == "http://localhost:8001"
    
    
    @pytest.mark.asyncio
    async def test_fetch_raw_data_http_error(self, repo):
        """
        TC-IR-009: Verificar que se maneja correctamente un error HTTP.
        """
        with patch("app.infrastructure.repositories.ingestion_repository_impl.httpx.AsyncClient") as mock_client:
            mock_client_instance = AsyncMock()
            mock_client_instance.__aenter__.return_value = mock_client_instance
            mock_client_instance.get = AsyncMock(
                side_effect=httpx.HTTPError("Connection failed")
            )
            mock_client.return_value = mock_client_instance
            
            # Act & Assert
            with pytest.raises(Exception) as exc_info:
                await repo.fetch_raw_data("dataset-001")
            
            assert "Falla al conectar" in str(exc_info.value)
    
    
    @pytest.mark.asyncio
    async def test_send_test_data_with_timeout(self, repo):
        """
        TC-IR-010: Verificar que se establece timeout para send_test_data.
        """
        request = TestIngestRequest(texto="test")
        
        with patch("app.infrastructure.repositories.ingestion_repository_impl.httpx.AsyncClient") as mock_client:
            mock_response = Mock()
            mock_response.json.return_value = {"status": "ok"}
            
            mock_client_instance = AsyncMock()
            mock_client_instance.__aenter__.return_value = mock_client_instance
            mock_client_instance.post = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_client_instance
            
            # Act
            await repo.send_test_data(request)
            
            # Assert
            # Verificar que se creó el cliente con timeout
            call_args = mock_client.call_args
            assert call_args[1]["timeout"] == 10.0
