

import os
from typing import Any, Dict, List

import httpx

from app.domain.analytics_client import IAnalyticsClient


#Implementacion ya que conoce urls http y librerias
class HttpAnalyticsClient(IAnalyticsClient):

    def __init__(self):
        self.base_url=os.getenv("MS_ANALYTICS_URL", "http://ms-analytics:8000")

    #aplicamos principio de liskov usamos obligatoriamente el metodo del dominio
    async def send_transformed_data(self, dataset_load_id: str, data: List[Dict[str, Any]]) -> bool:
        
        #ruta que va consumir el microservicio de analytics
        endpoint = f"{self.base_url}/api/v1/analytics/internal/sync/{dataset_load_id}"

        #empacamos
        payload={"data":data}

        #cliente sincronico
        try:
            async with httpx.AsyncClient()as client:
                response=await client.post(
                    endpoint,
                    json=payload,
                    timeout=15.0
                )
                #si nos devulve un error
                response.raise_for_status()
                print(f"Pipline ok{len(data)} registros enviados a ms-analytics")
                return True
        
        except httpx.HTTPError as e:
            print(f"Error fallo en la red enviado a ms-analytics:{e}")
            return False
        except Exception as e:
            print(f"Error inesperado {e}")
            return False
        
        

       
        