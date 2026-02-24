from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.domain.pokemon.external.schemas.base import (
    PokemonExternalBase,
    PokemonExternalBaseAbilitySchemaResponse,
    PokemonExternalBaseMoveSchemaResponse,
    PokemonExternalBaseTypeSchemaResponse,
)


class PokemonExternalByNameStatsSchemaResponse(BaseModel):
    model_config = ConfigDict(extra='ignore')

    stat: PokemonExternalBase
    base_stat: int


class PokemonExternalByNameSpritesDreamWorldSchema(BaseModel):
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


class PokemonExternalByNameSpritesOtherSchemaResponse(BaseModel):
    model_config = ConfigDict(extra='ignore')

    dream_world: Optional[PokemonExternalByNameSpritesDreamWorldSchema] = None


class PokemonExternalByNameSpritesSchemaResponse(BaseModel):
    model_config = ConfigDict(extra='ignore')

    other: Optional[PokemonExternalByNameSpritesOtherSchemaResponse] = None
    front_default: Optional[str] = None


class PokemonExternalByNameSchemaResponse(BaseModel):
    model_config = ConfigDict(extra='ignore')

    name: str
    order: int
    types: list[PokemonExternalBaseTypeSchemaResponse]
    moves: list[PokemonExternalBaseMoveSchemaResponse]
    stats: list[PokemonExternalByNameStatsSchemaResponse]
    height: int
    weight: int
    sprites: PokemonExternalByNameSpritesSchemaResponse
    abilities: list[PokemonExternalBaseAbilitySchemaResponse]
    base_experience: int


PokemonExternalByNameSchemaResponse.model_rebuild()
