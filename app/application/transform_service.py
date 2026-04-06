# Logica de Negocio (Use Case)
from typing import Any, Dict

from app.domain.repository.ingestion_repository import (
    IngestionRepository,  # ← clase pura (Port)
)
from app.schemas.ingestion import TestIngestRequest  # ← schema correcto


class TransformService:
    """USE CASE: Lógica de negocio de transformación.
    Solo depende del Port (IngestionRepository) → SOLID (DIP)"""

    def __init__(
        self,
        ingestion_repository: IngestionRepository,
        zone_repository: ZoneRepository  # ← nuevo Port inyectado
    ):
        self.ingestion_repository = ingestion_repository
        self.zone_repository = zone_repository
        self.ingestion_client = IngestionClient()  # cliente HTTP interno


    async def test_connection_to_ingestion(self, texto: str) -> Dict[str, Any]:
        """Prueba de conexión hacia ms-ingestion"""
        request = TestIngestRequest(texto=texto)
        return await self.ingestion_repository.send_test_data(request)
    

    async def process_zones(self, dataset_load_id: str, db: Session) -> List[str]:
        # Paso 1.1 — descarga CSV y extrae zonas únicas
        zones = await self.ingestion_client.get_zones_from_dataset(dataset_load_id)

        # Paso 1.2 — persiste en db-transformation
        self.zone_repository.save_zones(db, zones)

        return zones

    def get_zones(self, db: Session) -> List[str]:
       
        #Paso 1.3 — consulta las zonas ya procesadas desde db-transformation.
        #Retorna [] si no hay datos — nunca lanza excepción.
       
        return self.zone_repository.get_zones(db)