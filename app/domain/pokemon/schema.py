from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.shared.status_enum import StatusEnum


class PokemonSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    url: str
    name: str
    order: int
    status: StatusEnum
    external_image: str
    hp: Optional[int] = None
    image: Optional[str] = None
    speed: Optional[int] = None
    height: Optional[int] = None
    weight: Optional[int] = None
    attack: Optional[int] = None
    defense: Optional[int] = None
    habitat: Optional[str] = None
    is_baby: Optional[bool] = None
    shape_url: Optional[str] = None
    shape_name: Optional[str] = None
    is_mythical: Optional[bool] = None
    gender_rate: Optional[int] = None
    is_legendary: Optional[bool] = None
    capture_rate: Optional[int] = None
    hatch_counter: Optional[int] = None
    base_happiness: Optional[int] = None
    special_attack: Optional[int] = None
    base_experience: Optional[int] = None
    special_defense: Optional[int] = None
    evolution_chain_url: Optional[str] = None
    evolves_from_species: Optional[str] = None
    has_gender_differences: Optional[bool] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None


class PokemonListSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    results: list[PokemonSchema]


class CreatePokemonSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    url: str
    name: str
    order: int
    external_image: str
