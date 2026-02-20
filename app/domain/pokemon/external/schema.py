from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.domain.pokemon.schema import PokemonPublicSchema
from app.shared.status_enum import StatusEnum


class ExternalPokemonBase(BaseModel):
    model_config = ConfigDict(extra='ignore')

    url: str
    order: int
    name: str

class ExternalPokemonBaseList(ExternalPokemonBase):
    model_config = ConfigDict(extra='ignore')

    data: list[ExternalPokemonBase]

class PokemonBaseResponse(BaseModel):
    model_config = ConfigDict(extra='ignore')

    url: str
    name: str

class PokemonTypeResponse(BaseModel):
    model_config = ConfigDict(extra='ignore')

    slot: int
    type: PokemonBaseResponse

class PokemonMoveResponse(BaseModel):
    model_config = ConfigDict(extra='ignore')

    move: PokemonBaseResponse

class PokemonStatsResponse(BaseModel):
    model_config = ConfigDict(extra='ignore')

    stat: PokemonBaseResponse
    base_stat: int

class PokemonAbilityResponse(BaseModel):
    model_config = ConfigDict(extra='ignore')

    slot: int
    ability: PokemonBaseResponse
    is_hidden: bool

class PokemonSpritesDreamWorldSchema(BaseModel):
    model_config = ConfigDict(extra='ignore')

    back_gray: Optional[str] = None
    front_gray: Optional[str] = None
    back_shiny: Optional[str] = None
    front_shiny: Optional[str] = None
    back_female: Optional[str] = None
    front_female: Optional[str] = None
    back_default: Optional[str] = None
    front_default: Optional[str] = None
    back_transparent: Optional[str] = None
    front_transparent: Optional[str] = None
    back_shiny_female: Optional[str] = None
    front_shiny_female: Optional[str] = None
    back_shiny_transparent: Optional[str] = None
    front_shiny_transparent: Optional[str] = None

class PokemonSpritesOtherSchema(BaseModel):
    model_config = ConfigDict(extra='ignore')

    dream_world: Optional[PokemonSpritesDreamWorldSchema] = None

class PokemonSpritesSchema(BaseModel):
    model_config = ConfigDict(extra='ignore')

    other: Optional[PokemonSpritesOtherSchema] = None
    front_default: Optional[str] = None

class PokemonByNameSchema(BaseModel):
    model_config = ConfigDict(extra='ignore')

    name: str
    order: int
    types: list[PokemonTypeResponse]
    moves: list[PokemonMoveResponse]
    stats: list[PokemonStatsResponse]
    height: int
    weight: int
    sprites: PokemonSpritesSchema
    abilities: list[PokemonAbilityResponse]
    base_experience: int

class PokemonSpecieEvolutionChainResponse(BaseModel):
    model_config = ConfigDict(extra='ignore')

    url: str
    name: Optional[str] = None

class PokemonSpecieSchema(BaseModel):
    model_config = ConfigDict(extra='ignore')

    shape: Optional[PokemonBaseResponse] = None
    habitat: Optional[PokemonBaseResponse] = None
    is_baby: bool
    growth_rate: Optional[PokemonBaseResponse] = None
    gender_rate: int
    is_mythical: bool
    capture_rate: int
    is_legendary: bool
    hatch_counter: int
    base_happiness: int
    evolution_chain: Optional[PokemonSpecieEvolutionChainResponse] = None
    evolves_from_species: Optional[PokemonBaseResponse] = None
    has_gender_differences: bool

class FetchNameResultSchema(BaseModel):
    model_config = ConfigDict(extra='ignore')

    types: list[PokemonTypeResponse]
    moves: list[PokemonMoveResponse]
    abilities: list[PokemonAbilityResponse]
    growth_rate: Optional[PokemonBaseResponse] = None
    status: StatusEnum
    pokemon: PokemonPublicSchema

