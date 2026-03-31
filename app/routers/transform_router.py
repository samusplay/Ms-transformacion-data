from fastapi import APIRouter, Depends

from app.application.transform_service import TransformService

# ==================== INYECCIÓN DE DEPENDENCIAS ====================
# (las movemos aquí para evitar import circular)
from app.domain.repository.ingestion_repository import IngestionRepository
from app.infrastructure.repositories.ingestion_repository_impl import (
    IngestionRepositoryImpl,
)
from app.schemas.ingestion import TestIngestRequest


def get_ingestion_repository() -> IngestionRepository:
    return IngestionRepositoryImpl()

def get_transform_service(
    repo: IngestionRepository = Depends(get_ingestion_repository)
) -> TransformService:
    return TransformService(ingestion_repository=repo)
# ============================================================

transform_router = APIRouter(
    prefix="/api/v1/transform",
    tags=["Transformación"]
)

@transform_router.post("/test-ingestion")
async def test_connection_to_ingestion(
    request: TestIngestRequest,
    service: TransformService = Depends(get_transform_service)
):
    resultado = await service.test_connection_to_ingestion(request.texto)
    
    return {
        "status": "✅ Conexión exitosa",
        "mensaje": "ms-transform llamó correctamente a ms-ingestion",
        "respuesta_desde_ingestion": resultado
    }