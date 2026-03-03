from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.domain.pokemon.schema import PublicPokemonSchema
from app.shared.schemas import FilterPage


class CreatePokedexSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    hp: int
    wins: int
    level: int
    iv_hp: int
    ev_hp: int
    losses: int
    max_hp: int
    battles: int
    nickname: str
    iv_speed: int
    ev_speed: int
    iv_attack: int
    ev_attack: int
    iv_defense: int
    ev_defense: int
    experience: int
    iv_special_attack: int
    ev_special_attack: int
    iv_special_defense: int
    ev_special_defense: int
    discovered: bool = Field(default=False)
    discovered_at: Optional[datetime] = None
    pokemon_id: str
    trainer_id: str


class PokedexPublicSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    nickname: str
    hp: int
    wins: int
    level: int
    iv_hp: int
    ev_hp: int
    losses: int
    max_hp: int
    battles: int
    nickname: str
    iv_speed: int
    ev_speed: int
    iv_attack: int
    ev_attack: int
    iv_defense: int
    ev_defense: int
    experience: int
    iv_special_attack: int
    ev_special_attack: int
    iv_special_defense: int
    ev_special_defense: int
    discovered: bool = Field(default=False)
    discovered_at: Optional[datetime] = None
    pokemon: PublicPokemonSchema


class PokedexFilterPage(FilterPage):
    trainer_id: str
    nickname: Optional[str] = None
    discovered: Optional[bool] = None


class FindPokedexSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    trainer_id: str
    name: Optional[str] = None
    nickname: Optional[str] = None
    pokemon_id: Optional[str] = None
