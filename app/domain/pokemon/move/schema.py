from datetime import datetime

from pydantic import BaseModel


class MoveSchema(BaseModel):
    id: str
    pp: int
    url: str
    type: str
    name: str
    order: int
    power: int
    target: str
    effect: str
    priority: int
    accuracy: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None
    short_effect: str
    damage_class: str
    effect_chance: int | None = None