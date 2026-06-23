from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

# Importamos TU nuevo servicio y repositorio
from app.application.zone_service import ZoneService
from app.domain.repository.zone_repository import ZoneRepository
from app.infrastructure.database import get_db
from app.infrastructure.repositories.zone_repository_impl import ZoneRepositoryImpl

# ==================== INYECCIÓN DE DEPENDENCIAS ====================

def get_zone_repository() -> ZoneRepository:
    return ZoneRepositoryImpl()

def get_zone_service(
    zone_repo: ZoneRepository = Depends(get_zone_repository)
) -> ZoneService:
    return ZoneService(zone_repository=zone_repo)

# ==================== DEFINICIÓN DEL ROUTER ====================

zone_router = APIRouter(
    prefix="/api/v1/transform",
    tags=["Zonas"]
)

@zone_router.get("/zones", status_code=200)
def get_zones(
    db: Session = Depends(get_db),
    service: ZoneService = Depends(get_zone_service)
):
    """
    Endpoint para obtener las zonas disponibles y su cantidad de proyectos.
    Cumple CA 1 y CA 2 de la Historia de Usuario.
    """
    # El servicio se encarga de ir a la BD y armar la lista de diccionarios
    zones_summary = service.get_zones_summary(db)
    
    return {
        "success": True,
        "data": {
            "zones": zones_summary # Retorna el JSON estructurado o [] si no hay datos
        },
        "error": None
    }