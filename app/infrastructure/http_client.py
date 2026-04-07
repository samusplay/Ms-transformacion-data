import os

import httpx

AUDIT_API_URL = os.getenv("AUDIT_API_URL", "http://ms-audit:8000")

async def send_audit_event(dataset_load_id: str, trace_id: str):
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