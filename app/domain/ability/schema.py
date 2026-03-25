from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.shared.schemas import FilterPage


class PokemonAbilitySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    url: str
    name: str
    order: int
    slot: int
    is_hidden: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None


class CreatePokemonAbilitySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    url: str
    name: str
    order: int
    slot: int
    is_hidden: bool


class PokemonAbilityFilterPage(FilterPage):
    model_config = ConfigDict(from_attributes=True)

    name: Optional[str] = None
    slot: Optional[int] = None
    is_hidden: Optional[bool] = None
