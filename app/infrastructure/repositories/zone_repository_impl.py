from typing import List

from sqlalchemy.orm import Session

from app.domain.repository.zone_repository import ZoneRepository
from app.infrastructure.models.zone_orm import ZoneORM


class ZoneRepositoryImpl(ZoneRepository):


    def save_zones(self, db: Session, zones: List[str]) -> None:
        #Se usa merge() en vez de add() para evitar duplicados si el proceso se ejecuta más de una vez.
        for zone_name in zones:
            zone_orm = ZoneORM(name=zone_name)
            db.merge(zone_orm)  # Si ya existe la actualiza, si no la crea
        db.commit()

    def get_zones(self, db: Session) -> List[str]:
        
        #SELECT de todas las zonas.
        #Retorna lista plana de strings — nunca None.
        
        results = db.query(ZoneORM.name).all()
        return [row.name for row in results]  # [] si está vacío — nunca falla