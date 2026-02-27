from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.domain.pokemon.schema import PublicPokemonSchema


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
    discovered_at: datetime
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
    discovered_at: datetime
    pokemon: PublicPokemonSchema
