from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.domain.pokemon.model import Pokemon
from app.domain.pokemon.schema import PublicPokemonSchema
from app.domain.trainer.model import Trainer
from app.shared.schemas import FilterPage


class CreateCapturedPokemonSchema(BaseModel):
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
    captured_at: datetime
    pokemon: Pokemon | None = None
    trainer: Trainer | None = None
    pokemon_id: str
    trainer_id: str


class CapturedPokemonPublicSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
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
    captured_at: datetime
    pokemon: PublicPokemonSchema

class CapturedPokemonFilterPage(FilterPage):
    trainer_id: str
    nickname: Optional[str] = None


class CapturePokemonSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    nickname: Optional[str] = None
    pokemon_name: str