from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.domain.pokemon.schema import PublicPokemonSchema
from app.models.pokemon import Pokemon
from app.models.pokemon_move import PokemonMove
from app.models.trainer import Trainer


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
    speed: int
    iv_speed: int
    ev_speed: int
    attack: int
    iv_attack: int
    ev_attack: int
    defense: int
    iv_defense: int
    ev_defense: int
    experience: int
    special_attack: int
    iv_special_attack: int
    ev_special_attack: int
    special_defense: int
    iv_special_defense: int
    ev_special_defense: int
    captured_at: datetime
    pokemon: Pokemon | None = None
    trainer: Trainer | None = None
    pokemon_id: str
    trainer_id: str
    formula: str


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
    speed: int
    iv_speed: int
    ev_speed: int
    attack: int
    iv_attack: int
    ev_attack: int
    defense: int
    iv_defense: int
    ev_defense: int
    experience: int
    special_attack: int
    iv_special_attack: int
    ev_special_attack: int
    special_defense: int
    iv_special_defense: int
    ev_special_defense: int
    captured_at: datetime
    moves: list[PokemonMove] = []
    pokemon: PublicPokemonSchema


class CapturePokemonSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    nickname: Optional[str] = None
    pokemon_name: str


class FindCapturePokemonSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    trainer_id: str
    name: Optional[str] = None
    nickname: Optional[str] = None
    pokemon_id: Optional[str] = None


class CapturePokemonResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    error: bool
    error_detail: Optional[str] = None
    captured_pokemon: Optional[CapturedPokemonPublicSchema] = None


class PartialCapturedPokemonSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    hp: Optional[int] = None
    wins: Optional[int] = None
    losses: Optional[int] = None
    level: Optional[int] = None
    attack: Optional[int] = None
    defense: Optional[int] = None
    experience: Optional[int] = None
    speed: Optional[int] = None
    special_attack: Optional[int] = None
    special_defense: Optional[int] = None


class CapturePokemonHealSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    all: Optional[bool] = False
    pokemons: Optional[list[str]] = []
