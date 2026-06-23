from pydantic import BaseModel

class TransformMetricsResponse(BaseModel):
    transformed_records: int
    execution_time_ms: float
