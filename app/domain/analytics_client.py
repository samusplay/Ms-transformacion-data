
#principio Dip solid
from abc import ABC, abstractmethod
from typing import Any, Dict, List


@abstractmethod
class IAnalyticsClient(ABC):
    #Puerto de salida para enviar datos

#metodo puro  para enviar los datos analytcs el dataset de json
    async def send_transformed_data(self,dataset_load_id:str,data:List[Dict[str, Any]])->bool:
        pass