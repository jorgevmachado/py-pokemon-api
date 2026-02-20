from datetime import datetime
from typing import Optional

from pydantic import ConfigDict, BaseModel

from app.domain.pokemon.ability.schema import AbilitySchema
from app.domain.pokemon.growth_rate.schema import GrowthRateSchema
from app.domain.pokemon.move.schema import MoveSchema
from app.domain.pokemon.type.schema import PokemonTypeSchema
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
    deleted_at: datetime | None = None
    growth_rate_id: Optional[str] = None
    growth_rate: GrowthRateSchema | None = None
    moves: list[MoveSchema] = []
    types: list[PokemonTypeSchema] = []
    abilities: list[AbilitySchema] = []

class PokemonPublicSchema(PokemonSchema):
    model_config = ConfigDict(from_attributes=True)
    evolutions: list[PokemonSchema] = []

class PokemonPublicListSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    results: list[PokemonPublicSchema]
