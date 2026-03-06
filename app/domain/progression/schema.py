from pydantic import BaseModel


class ProgressionResult(BaseModel):
    hp: int
    wins: int
    level: int
    iv_hp: int
    ev_hp: int
    losses: int
    max_hp: int
    battles: int
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


class ProgressionListResult(BaseModel):
    level_up: bool
    attacker_progression: ProgressionResult
    defender_progression: ProgressionResult


class StatBlock(BaseModel):
    hp: int
    speed: int
    attack: int
    defense: int
    special_attack: int
    special_defense: int
