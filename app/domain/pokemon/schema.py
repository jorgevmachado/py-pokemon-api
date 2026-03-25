from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.domain.ability.schema import PokemonAbilitySchema
from app.domain.growth_rate.schema import PokemonGrowthRateSchema
from app.domain.move.schema import PokemonMoveSchema
from app.domain.pokemon.external.schemas import (
    PokemonExternalBase,
    PokemonExternalBaseAbilitySchemaResponse,
    PokemonExternalBaseMoveSchemaResponse,
    PokemonExternalBaseTypeSchemaResponse,
)
from app.domain.type.model import PokemonType
from app.domain.type.schema import PokemonTypeSchema
from app.models.pokemon import Pokemon
from app.models.pokemon_ability import PokemonAbility
from app.models.pokemon_growth_rate import PokemonGrowthRate
from app.models.pokemon_move import PokemonMove
from app.shared.enums.status_enum import StatusEnum
from app.shared.schemas import FilterPage


class PokemonEvolutionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    url: str
    name: str
    order: int
    status: StatusEnum
    external_image: str
    image: Optional[str] = None
    types: list[PokemonTypeSchema] = []


class PublicPokemonSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    url: str
    name: str
    order: int
    status: StatusEnum
    external_image: str
    hp: Optional[int] = None
    image: Optional[str] = None
    speed: Optional[int] = None
    height: Optional[int] = None
    weight: Optional[int] = None
    attack: Optional[int] = None
    defense: Optional[int] = None
    habitat: Optional[str] = None
    is_baby: Optional[bool] = None
    shape_url: Optional[str] = None
    shape_name: Optional[str] = None
    is_mythical: Optional[bool] = None
    gender_rate: Optional[int] = None
    is_legendary: Optional[bool] = None
    capture_rate: Optional[int] = None
    hatch_counter: Optional[int] = None
    base_happiness: Optional[int] = None
    special_attack: Optional[int] = None
    base_experience: Optional[int] = None
    special_defense: Optional[int] = None
    evolution_chain_url: Optional[str] = None
    evolves_from_species: Optional[str] = None
    has_gender_differences: Optional[bool] = None
    moves: list[PokemonMove] = []
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None


class PokemonSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    url: str
    name: str
    order: int
    status: StatusEnum
    external_image: str
    hp: Optional[int] = None
    image: Optional[str] = None
    speed: Optional[int] = None
    height: Optional[int] = None
    weight: Optional[int] = None
    attack: Optional[int] = None
    defense: Optional[int] = None
    habitat: Optional[str] = None
    is_baby: Optional[bool] = None
    shape_url: Optional[str] = None
    shape_name: Optional[str] = None
    is_mythical: Optional[bool] = None
    gender_rate: Optional[int] = None
    is_legendary: Optional[bool] = None
    capture_rate: Optional[int] = None
    hatch_counter: Optional[int] = None
    base_happiness: Optional[int] = None
    special_attack: Optional[int] = None
    base_experience: Optional[int] = None
    special_defense: Optional[int] = None
    evolution_chain_url: Optional[str] = None
    evolves_from_species: Optional[str] = None
    has_gender_differences: Optional[bool] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    types: list[PokemonTypeSchema] = []
    moves: list[PokemonMoveSchema] = []
    abilities: list[PokemonAbilitySchema] = []
    evolutions: list[PokemonEvolutionSchema] = []
    growth_rate: Optional[PokemonGrowthRateSchema] = None

    def serialize(self) -> dict:
        serialized = self.model_dump(mode='json')
        if 'evolutions' in serialized and serialized['evolutions']:
            serialized['evolutions'] = [
                PokemonEvolutionSchema.model_validate(evo).model_dump(mode='json')
                for evo in serialized['evolutions']
            ]
        if 'types' in serialized and serialized['types']:
            serialized['types'] = [
                PokemonTypeSchema.model_validate(pt).model_dump(mode='json')
                for pt in serialized['types']
            ]
        if 'abilities' in serialized and serialized['abilities']:
            serialized['abilities'] = [
                PokemonAbilitySchema.model_validate(ab).model_dump(mode='json')
                for ab in serialized['abilities']
            ]
        if 'moves' in serialized and serialized['moves']:
            serialized['moves'] = [
                PokemonMoveSchema.model_validate(mv).model_dump(mode='json')
                for mv in serialized['moves']
            ]
        if 'growth_rate' in serialized and serialized['growth_rate']:
            serialized['growth_rate'] = PokemonGrowthRateSchema.model_validate(
                serialized['growth_rate']
            ).model_dump(mode='json')
        return serialized


class PokemonListSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    results: list[PokemonSchema]


class CreatePokemonSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    url: str
    name: str
    order: int
    external_image: str


class GeneratePokemonRelationshipSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    types: list[PokemonExternalBaseTypeSchemaResponse]
    moves: list[PokemonExternalBaseMoveSchemaResponse]
    abilities: list[PokemonExternalBaseAbilitySchemaResponse]
    growth_rate: Optional[PokemonExternalBase] = None


class GeneratePokemonRelationshipSchemaResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    status: StatusEnum
    types: list[PokemonType]
    moves: list[PokemonMove]
    abilities: list[PokemonAbility]
    growth_rate: Optional[PokemonGrowthRate] = None


class FirstPokemonSchemaResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    pokemon: Optional[Pokemon] = None
    pokemons: list[Pokemon] = []


class PokemonFilterPage(FilterPage):
    model_config = ConfigDict(from_attributes=True)

    name: Optional[str] = None
    status: Optional[StatusEnum] = None
