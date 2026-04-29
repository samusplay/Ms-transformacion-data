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
    """
    zones_summary = service.get_zones_summary(db)
    
    return {
        "success": True,
        "data": {
            "zones": zones_summary
        },
        "error": None
    }

@zone_router.get("/zones/metrics", status_code=200)
def get_zone_metrics(
    names: str,
    db: Session = Depends(get_db)
):
    """
    Endpoint para obtener las métricas detalladas de zonas específicas.
    Recibe: ?names=VALLE,SANTANDER
    """
    from app.infrastructure.models import ZoneAnalytics
    from sqlalchemy import func

    zone_names = [n.strip().upper() for n in names.split(",") if n.strip()]
    
    results = []
    for zone_name in zone_names:
        # Traemos la última entrada de esa zona
        zone = (
            db.query(ZoneAnalytics)
            .filter(ZoneAnalytics.zone_name == zone_name)
            .order_by(ZoneAnalytics.id.desc())
            .first()
        )
        if zone:
            results.append({
                "name": zone.zone_name,
                "zone_code": zone.zone_code,
                "region": zone.region,
                "metrics": zone.metrics or {}
            })
    
    return {
        "success": True,
        "data": {"zones": results},
        "error": None
    }