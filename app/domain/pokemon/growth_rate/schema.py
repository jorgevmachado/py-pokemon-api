from datetime import datetime

from pydantic import BaseModel

class GrowthRateSchema(BaseModel):
    id: str
    url: str
    name: str
    formula: str
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime