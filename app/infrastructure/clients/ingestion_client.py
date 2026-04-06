import io
import os
from typing import List

import httpx
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

class IngestionClient:
    """
    Cliente HTTP interno que se comunica con ms-ingestion.
    Responsabilidad única (SOLID - S): solo sabe cómo hablar
    con ms-ingestion y extraer zonas del CSV — nada más.
    """

    def __init__(self):
        self.base_url = os.getenv("INGESTION_SERVICE_URL", "").rstrip("/")
        if not self.base_url:
            raise ValueError("INGESTION_SERVICE_URL no encontrado en .env")

    async def get_zones_from_dataset(self, dataset_load_id: str) -> List[str]:
        """
        Paso 1.1 del entregable:
        1. Descarga el CSV validado desde ms-ingestion
        2. Extrae la columna de zonas con Pandas
        3. Aplica drop_duplicates() para zonas únicas
        
        Retorna una lista plana de strings ej: ["Zona Norte", "Zona Sur"]
        """
        url = f"{self.base_url}/api/v1/ingesta/datasets/{dataset_load_id}/file"

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)
            response.raise_for_status()  # Lanza excepción si ms-ingestion falla

        # Carga el contenido del CSV en memoria con Pandas
        # io.BytesIO evita guardar el archivo en disco
        df = pd.read_csv(io.BytesIO(response.content))

        # Detecta la columna de zonas — intenta zone_name primero, luego zone_code
        if "zone_name" in df.columns:
            zone_column = "zone_name"
        elif "zone_code" in df.columns:
            zone_column = "zone_code"
        else:
            raise ValueError(
                f"El CSV no tiene columna 'zone_name' ni 'zone_code'. "
                f"Columnas encontradas: {list(df.columns)}"
            )

        # drop_duplicates() garantiza zonas únicas — dropna() elimina valores vacíos
        zones = (
            df[zone_column]
            .dropna()
            .drop_duplicates()
            .tolist()
        )

        return [str(zone) for zone in zones]  # Garantiza que todos sean strings