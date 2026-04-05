from pydantic import BaseModel
from typing import Any, Optional

class StandardResponse(BaseModel):
    success: bool
    data: Any
    error: Optional[str] = None
    trace_id: str = ""
