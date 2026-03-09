from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.domain.pokemon.external.schemas import PokemonExternalBase


class PokemonExternalEvolutionsDetailsSchemaResponse(BaseModel):
    model_config = ConfigDict(extra='ignore')
    base_form_id: Optional[int] = None
    gender: Optional[int] = None
    held_item: Optional[PokemonExternalBase] = None
    item: Optional[PokemonExternalBase] = None
    known_move: Optional[PokemonExternalBase] = None
    known_move_type: Optional[PokemonExternalBase] = None
    location: Optional[PokemonExternalBase] = None
    min_affection: Optional[int] = None
    min_beauty: Optional[int] = None
    min_damage_taken: Optional[int] = None
    min_happiness: Optional[int] = None
    min_level: Optional[int] = None
    min_move_count: Optional[int] = None
    min_steps: Optional[int] = None
    needs_multiplayer: Optional[bool] = False
    needs_overworld_rain: Optional[bool] = False
    party_species: Optional[PokemonExternalBase] = None
    party_type: Optional[PokemonExternalBase] = None
    region: Optional[PokemonExternalBase] = None
    region_id: Optional[str] = None
    relative_physical_stats: Optional[int] = None
    time_of_day: Optional[str] = None
    trade_species: Optional[PokemonExternalBase] = None
    trigger: PokemonExternalBase
    turn_upside_down: Optional[bool] = False
    used_move: Optional[PokemonExternalBase] = None


class PokemonExternalEvolutionChainEvolvesToSchema(BaseModel):
    model_config = ConfigDict(extra='ignore')
    evolution_details: Optional[list[PokemonExternalEvolutionsDetailsSchemaResponse]] = []
    is_baby: Optional[bool] = False
    species: PokemonExternalBase
    evolves_to: Optional[list['PokemonExternalEvolutionChainEvolvesToSchema']] = []


class PokemonExternalEvolutionChainEvolvesToSchemaResponse(BaseModel):
    model_config = ConfigDict(extra='ignore')
    evolution_details: Optional[list[PokemonExternalEvolutionsDetailsSchemaResponse]] = []
    is_baby: Optional[bool] = False
    species: PokemonExternalBase
    evolves_to: Optional[list[PokemonExternalEvolutionChainEvolvesToSchema]] = []


class PokemonExternalEvolutionChainSchemaResponse(BaseModel):
    model_config = ConfigDict(extra='ignore')

    evolution_details: Optional[list[PokemonExternalEvolutionsDetailsSchemaResponse]] = []
    evolves_to: Optional[list[PokemonExternalEvolutionChainEvolvesToSchemaResponse]] = []
    is_baby: Optional[bool] = False
    species: PokemonExternalBase


class PokemonExternalEvolutionSchemaResponse(BaseModel):
    model_config = ConfigDict(extra='ignore')
    id: int
    chain: PokemonExternalEvolutionChainSchemaResponse
    baby_trigger_item: Optional[PokemonExternalBase] = None
