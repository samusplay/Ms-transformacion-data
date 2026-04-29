import os
from typing import Any, Dict

import httpx
from dotenv import load_dotenv

from app.domain.repository.ingestion_repository import IngestionRepository
from app.schemas.ingestion import TestIngestRequest  # ← nombre correcto

load_dotenv()

class IngestionRepositoryImpl(IngestionRepository):
    """ADAPTER / IMPLEMENTACIÓN: Llama por REST a ms-ingestion"""

    def __init__(self):
        self.base_url = os.getenv("INGESTION_SERVICE_URL")
        if not self.base_url:
            raise ValueError("❌ INGESTION_SERVICE_URL no encontrado en .env")
        self.base_url = self.base_url.rstrip("/")

    async def send_test_data(self, request: TestIngestRequest) -> Dict[str, Any]:
        url = f"{self.base_url}/test-hexagonal"

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                url,
                json=request.model_dump(),
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json()

    async def fetch_raw_data(self, dataset_load_id: str) -> Dict[str, Any]:
         # Limpiamos base_url por si acaso trae barras al final
         base = self.base_url.rstrip("/")
         # Construimos la ruta estándar interna del microservicio
         url = f"{base}/api/v1/ingesta/datasets/{dataset_load_id}/raw"
         async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                raise Exception(f"Falla al conectar con MS Ingesta en la url {url}: {str(e)}")