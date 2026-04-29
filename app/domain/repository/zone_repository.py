
from abc import ABC, abstractmethod
from typing import Any, Dict, List


class ZoneRepository(ABC):
    @abstractmethod
    def save_zones(self, db, zones: List[str]) -> None:
        """Guarda una lista de zonas únicas (Lo dejamos por si acaso)"""
        pass

    @abstractmethod
    def get_zones(self, db) -> List[str]:
        """Retorna todas las zonas planas (El método original)"""
        pass

    @abstractmethod
    def get_zone_summaries(self, db) -> List[Dict[str, Any]]:
        """
        Retorna un listado de zonas con su conteo de proyectos.
        Ejemplo esperado: [{"name": "VALLE", "record_count": 5}]
        """
        pass