from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.domain.pokemon.external.schemas import (
    PokemonExternalBase,
    PokemonExternalBaseAbilitySchemaResponse,
    PokemonExternalBaseMoveSchemaResponse,
    PokemonExternalBaseTypeSchemaResponse,
)
from app.domain.pokemon.schema import PokemonSchema


class PokemonFetchOneSchemaResponse(BaseModel):
    model_config = ConfigDict(extra='ignore')
    pokemon: PokemonSchema
    types: list[PokemonExternalBaseTypeSchemaResponse]
    moves: list[PokemonExternalBaseMoveSchemaResponse]
    abilities: list[PokemonExternalBaseAbilitySchemaResponse]
    growth_rate: Optional[PokemonExternalBase] = None
