from datetime import datetime

from pydantic import BaseModel

class AbilitySchema(BaseModel):
    id: str
    url: str
    name: str
    order: int
    slot: int
    is_hidden: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None