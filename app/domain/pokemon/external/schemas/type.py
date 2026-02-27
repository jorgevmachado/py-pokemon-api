from pydantic import BaseModel, ConfigDict

from app.domain.pokemon.external.schemas import PokemonExternalBase


class PokemonExternalTypeDamageRelationsSchemaResponse(BaseModel):
    model_config = ConfigDict(extra='ignore')
    double_damage_from: list[PokemonExternalBase]
    double_damage_to: list[PokemonExternalBase]
    half_damage_from: list[PokemonExternalBase]
    half_damage_to: list[PokemonExternalBase]


class PokemonExternalTypeGameIndicesSchemaResponse(BaseModel):
    model_config = ConfigDict(extra='ignore')

    game_index: int
    generation: PokemonExternalBase


class PokemonExternalTypeLanguageSchemaResponse(BaseModel):
    model_config = ConfigDict(extra='ignore')

    language: PokemonExternalBase
    name: str


class PokemonExternalTypeSchemaResponse(BaseModel):
    model_config = ConfigDict(extra='ignore')

    damage_relations: PokemonExternalTypeDamageRelationsSchemaResponse
    game_indices: list[PokemonExternalTypeGameIndicesSchemaResponse]
    generation: PokemonExternalBase
    id: int
    move_damage_class: PokemonExternalBase
    moves: list[PokemonExternalBase]
    names: list[PokemonExternalTypeLanguageSchemaResponse]
