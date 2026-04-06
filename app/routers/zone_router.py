from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.application.transform_service import TransformService
from app.domain.repository.ingestion_repository import IngestionRepository
from app.domain.repository.zone_repository import ZoneRepository
from app.infrastructure.database import get_db
from app.infrastructure.repositories.ingestion_repository_impl import IngestionRepositoryImpl
from app.infrastructure.repositories.zone_repository_impl import ZoneRepositoryImpl

#Se inyectan las dependencias

def get_ingestion_repository() -> IngestionRepository:
    return IngestionRepositoryImpl()

def get_zone_repository() -> ZoneRepository:
    return ZoneRepositoryImpl()

def get_transform_service(
    ingestion_repo: IngestionRepository = Depends(get_ingestion_repository),
    zone_repo: ZoneRepository = Depends(get_zone_repository)
) -> TransformService:
    return TransformService(
        ingestion_repository=ingestion_repo,
        zone_repository=zone_repo
    )


zone_router = APIRouter(
    prefix="/api/v1/transform",
    tags=["Zonas"]
)

@zone_router.get("/zones", status_code=200)
def get_zones(
    db: Session = Depends(get_db),
    service: TransformService = Depends(get_transform_service)
):
   
    #Paso 1.3 endpoint GET /zones.
    
    #CA 1: Si hay zonas en db-transformation retorna la lista.
    #CA 2: Si la BD está vacía retorna [] — NUNCA un 404. Siempre retorna 200.
   
    zones = service.get_zones(db)

    return {
        "success": True,
        "data": {
            "zones": zones  # [] si está vacío — cumple CA 2
        },
        "error": None
    }