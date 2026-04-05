import io
import os
from typing import List

import httpx
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

class IngestionClient:


    def __init__(self):
        self.base_url = os .getenv ("INGESTION_SERVICE_URL", "").rstrip("/")
        if not self.base_url:
            raise ValueError("INGESTION_SERVICE_URL no encontrado en .env")
        
    async def get_zones_from_dataset (self, dataset_load_id: str )-> List[str]:

        url= f"{self.base_url}/api/v1/ingesta/datasets/{dataset_load_id}/file"

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)
            response.raise_for_status() 

        df = pd.read_csv(io.BytesIO(response.content))

        if "zone_name" in df.columns:
            zone_column = "zone_name"
        elif "zone_code" in df.columns:
            zone_column = "zone_code"

        else:
            raise ValueError(
                f"El CSV no tiene columna 'zone_name' ni 'zone_code'. "
                f"Columnas encontradas: {list(df.columns)}"
            )
        
        zones = (
            df[zone_column]
            .dropna()
            .drop_duplicates()
            .tolist()
        )

        return [str(zone) for zone in zones]  # Garantiza que todos sean strings