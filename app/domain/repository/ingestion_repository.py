from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict

# ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←
from app.schemas.ingestion import TestIngestRequest  # ← nombre correcto

# ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←

class IngestionRepository(ABC):
    """PORT: Interfaz pura"""

    @abstractmethod
    async def send_test_data(self, request: TestIngestRequest) -> Dict[str, Any]:
        """Método de prueba para llamar a ms-ingestion"""
        pass

    @abstractmethod
    async def fetch_raw_data(self, dataset_load_id: int) -> Dict[str, Any]:
        """Obtiene los registros del dataset validados por ms-ingestion"""
        pass