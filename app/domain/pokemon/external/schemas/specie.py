from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.domain.pokemon.external.schemas.base import PokemonExternalBase


class PokemonSpecieEvolutionChainResponse(BaseModel):
    model_config = ConfigDict(extra='ignore')

    url: str
    name: Optional[str] = None


class PokemonExternalSpecieSchemaResponse(BaseModel):
    model_config = ConfigDict(extra='ignore')

    name: str
    shape: Optional[PokemonExternalBase] = None
    habitat: Optional[PokemonExternalBase] = None
    is_baby: bool
    growth_rate: Optional[PokemonExternalBase] = None
    gender_rate: int
    is_mythical: bool
    capture_rate: int
    is_legendary: bool
    hatch_counter: int
    base_happiness: int
    evolution_chain: Optional[PokemonSpecieEvolutionChainResponse] = None
    evolves_from_species: Optional[PokemonExternalBase] = None
    has_gender_differences: bool
