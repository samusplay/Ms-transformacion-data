from pydantic import BaseModel


class TestIngestRequest(BaseModel):
    """Esquema que usaremos para enviar datos a ms-ingestion"""
    texto: str