from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.domain.pokemon.external.schemas import PokemonExternalBase


class PokemonExternalEvolutionsDetailsSchemaResponse(BaseModel):
    model_config = ConfigDict(extra='ignore')
    base_form_id: Optional[int] = None
    gender: Optional[str] = None
    held_item: Optional[str] = None
    item: Optional[str] = None
    known_move: Optional[str] = None
    known_move_type: Optional[str] = None
    location: Optional[str] = None
    min_affection: Optional[str] = None
    min_beauty: Optional[str] = None
    min_damage_taken: Optional[str] = None
    min_happiness: Optional[str] = None
    min_level: Optional[int] = None
    min_move_count: Optional[str] = None
    min_steps: Optional[str] = None
    needs_multiplayer: Optional[bool] = False
    needs_overworld_rain: Optional[bool] = False
    party_species: Optional[str] = None
    party_type: Optional[str] = None
    region_id: Optional[str] = None
    relative_physical_stats: Optional[str] = None
    time_of_day: Optional[str] = None
    trade_species: Optional[str] = None
    trigger: PokemonExternalBase
    turn_upside_down: Optional[bool] = False
    used_move: Optional[str] = None


class PokemonExternalEvolutionChainEvolvesToSchema(BaseModel):
    model_config = ConfigDict(extra='ignore')
    evolution_details: Optional[list[PokemonExternalEvolutionsDetailsSchemaResponse]] = []
    is_baby: Optional[bool] = False
    species: PokemonExternalBase


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
    baby_trigger_item: dict[str, str] | None = None
