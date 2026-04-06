from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List


class ZoneRepository(ABC):
   
    @abstractmethod
    def save_zones(self, db, zones: List[str]) -> None:
        "Guarda una lista de zonas únicas en db-transformation"
        pass

    @abstractmethod
    def get_zones(self, db) -> List[str]:
        "Retorna todas las zonas almacenadas en db-transformation"
        pass