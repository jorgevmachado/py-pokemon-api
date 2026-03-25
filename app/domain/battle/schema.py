from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.domain.progression.schema import StatBlock
from app.models.pokemon import Pokemon
from app.models.pokemon_move import PokemonMove


class AttackResult(BaseModel):
    damage: int
    remaining_hp: int
    fainted: bool
    critical: bool
    effectiveness: float
    stab: bool
    missed: bool
    error: Optional[bool] = False
    error_detail: Optional[str] = None
    applied_status: Optional[str] = None


class BattleSchema(BaseModel):
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
    formula: str

    pokemon: Pokemon


class ValidatPreconditions(BaseModel):
    error: bool
    error_detail: Optional[str] = None


class BattlePokemonSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    trainer_pokemon: str
    trainer_pokemon_move: str
    opponent_pokemon: str
    opponent_pokemon_move: Optional[str] = None


class GetBattlePokemonSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    pokemon: BattleSchema
    pokemon_move: Optional[PokemonMove] = None


class BattleResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    winner: str
    fainted: bool
    level_up: bool
    missed: bool
    attack_damage: int
    defense_damage: int
    remaining_hp: int
    previous_stats: StatBlock
    previous_level: int
    previous_experience: int
    current_stats: StatBlock
    current_level: int
    current_experience: int
    critical: bool
    stab: bool
    applied_status: Optional[str] = None
