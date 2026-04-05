import httpx
import os
import uuid

INGESTION_API_URL = os.getenv("INGESTION_API_URL", "http://ms-ingestion:8000")
AUDIT_API_URL = os.getenv("AUDIT_API_URL", "http://ms-audit:8004")

async def fetch_raw_data_from_ingestion(dataset_load_id: int):
    """Obtiene los registros crudos del dataset validados por el ms-ingestion."""
    # En CA1 dice extraer los registros crudos
    # Usaremos una URL ficticia predeterminada basada en los lineamientos
    url = f"{INGESTION_API_URL}/api/v1/datasets/{dataset_load_id}/raw"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise Exception(f"Falla al conectar con MS Ingesta en la url {url}: {str(e)}")

async def send_audit_event(dataset_load_id: int, trace_id: str):
    """Envia evento de TRANSFORMATION_COMPLETED a ms-audit (CA 5)"""
    url = f"{AUDIT_API_URL}/api/v1/events"
    payload = {
        "event_type": "TRANSFORMATION_COMPLETED",
        "service_name": "ms-transform",
        "reference_id": str(dataset_load_id),
        "event_summary": "Finalizó exitosamente el proceso de limpieza y guardado",
        "trace_id": trace_id
    }
    
    # Fire and forget o await, dependiendo de diseño (lo haremos await simple aquí)
    async with httpx.AsyncClient() as client:
        try:
            await client.post(url, json=payload, timeout=5.0)
        except Exception as e:
            print(f"⚠️ Error enviando evento a auditoría: {e}")
