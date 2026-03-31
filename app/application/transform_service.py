# Logica de Negocio (Use Case)
from typing import Any, Dict

from app.domain.repository.ingestion_repository import (
    IngestionRepository,  # ← clase pura (Port)
)
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