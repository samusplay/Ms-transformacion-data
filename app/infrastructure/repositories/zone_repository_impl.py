from typing import Any, Dict, List

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.domain.repository.zone_repository import ZoneRepository

# Tabla maestra
from app.infrastructure.models import ZoneAnalytics


class ZoneRepositoryImpl(ZoneRepository):
    def save_zones(self, db: Session, zones: List[str]) -> None:
        pass

    def get_zones(self, db: Session) -> List[str]:
        # Retorna la lista plana de zonas unicas
        results = db.query(ZoneAnalytics.zone_name).distinct().all()
        return [row[0] for row in results if row[0] is not None]

    def get_zone_summaries(self, db: Session) -> List[Dict[str, Any]]:
        try:
            results = (
                db.query(
                    ZoneAnalytics.zone_name,
                    func.count(ZoneAnalytics.id).label("record_count"),
                )
                .group_by(ZoneAnalytics.zone_name)
                .all()
            )

            return [
                {"name": row.zone_name, "record_count": row.record_count}
                for row in results
                if row.zone_name is not None
            ]
        except Exception as e:
            print(f"Error consultando resúmenes de zonas: {e}")
            # Si falla la BD, d
