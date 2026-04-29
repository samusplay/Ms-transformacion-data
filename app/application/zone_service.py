from typing import Any, Dict, List

from sqlalchemy.orm import Session

from app.domain.repository.zone_repository import ZoneRepository


class ZoneService:
    def __init__(self, zone_repository: ZoneRepository):
        # Inyectamos la interfaz del repositorio (El Puerto)
        self.zone_repository = zone_repository

    def get_zones_summary(self, db: Session) -> List[Dict[str, Any]]:
        """
        Retorna el resumen analítico de las zonas procesadas.
        Ejemplo: [{"name": "VALLE", "record_count": 5}]
        """
        return self.zone_repository.get_zone_summaries(db)