from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.shared.schemas import FilterPage


class PokemonMoveSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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
    short_effect: str
    damage_class: str
    effect_chance: int | None = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None


class CreatePokemonMoveSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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
    short_effect: str
    damage_class: str
    effect_chance: int | None = None


class PokemonMoveFilterPage(FilterPage):
    pp: Optional[int] = None
    type: Optional[str] = None
    name: Optional[str] = None
    order: Optional[int] = None
    power: Optional[int] = None
    target: Optional[str] = None
    effect: Optional[str] = None
    priority: Optional[int] = None
    accuracy: Optional[int] = None
    short_effect: Optional[str] = None
    damage_class: Optional[str] = None
    effect_chance: Optional[int] = None
