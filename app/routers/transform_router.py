import asyncio
import uuid

# Librerías de terceros
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

# Módulos locales: Aplicación y Dominio
from app.application.transform_service import TransformService
from app.domain.repository.ingestion_repository import IngestionRepository

# Módulos locales: Infraestructura
from app.infrastructure.database import get_db
from app.infrastructure.http_client import send_audit_event
from app.infrastructure.repositories.ingestion_repository_impl import (
    IngestionRepositoryImpl,
)

# Módulos locales: Schemas (Contratos)
from app.schemas.base_response import StandardResponse
from app.schemas.ingestion import TestIngestRequest
from app.schemas.transform import TransformMetricsResponse

# ==================== INYECCIÓN DE DEPENDENCIAS ====================

def get_ingestion_repository() -> IngestionRepository:
    """Instancia el adaptador de infraestructura"""
    return IngestionRepositoryImpl()

def get_transform_service(
    repo: IngestionRepository = Depends(get_ingestion_repository)
) -> TransformService:
    """Inyecta el repositorio en el caso de uso (TransformService)"""
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
    """Endpoint legado original de testeo de orquestación (Hexagonal)"""
    resultado = await service.test_connection_to_ingestion(request.texto)
    
    return {
        "status": "✅ Conexión exitosa",
        "mensaje": "ms-transform llamó correctamente a ms-ingestion",
        "respuesta_desde_ingestion": resultado
    }


# ==================== ENDPOINTS SPRINT 1 ====================

@transform_router.get("/health", response_model=StandardResponse)
async def health_check():
    """HU-08: Verificar estado del microservicio MS-Transform"""
    trace_id = str(uuid.uuid4())
    return StandardResponse(
        success=True,
        data={"status": "OK", "service": "ms-transform"},
        error=None,
        trace_id=trace_id
    )

@transform_router.post("/{dataset_load_id}", response_model=StandardResponse)
async def process_dataset(
    dataset_load_id: str,
    db: Session = Depends(get_db),
    service: TransformService = Depends(get_transform_service)
):
    """HU-07: Iniciar el proceso de ETL en memoria y persistir"""
    trace_id = str(uuid.uuid4())
    try:
        # Llamar al flujo de servicio aplicativo (CA 1, CA 2 y CA 3)
        metrics = await service.process_dataset(dataset_load_id, db)
        
        # Enviar evento de auditoria en background silenciosamente (CA 5)
        # Delegamos a traves de event loop para no frenar la respuesta
        asyncio.create_task(send_audit_event(dataset_load_id, trace_id))

        # Responder conforme al CA 4
        return StandardResponse(
            success=True,
            data=TransformMetricsResponse(**metrics),
            error=None,
            trace_id=trace_id
        )
    except ValueError as ve:
        # Error de negocio (dataset vacio o fallo de regla)
        return StandardResponse(
            success=False,
            data=None,
            error=str(ve),
            trace_id=trace_id
        )
    except Exception as e:
        # Control de errores sin exponer detalles innecesarios (Seguridad basica punto 8.1)
        print(f"ERROR CRITICO EN TRANSFORMACION: {e}")
        return StandardResponse(
            success=False,
            data=None,
            error="Ocurrió un error interno procesando el dataset estructurado.",
            trace_id=trace_id
        )