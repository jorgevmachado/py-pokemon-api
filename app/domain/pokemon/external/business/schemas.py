from typing import Optional

from pydantic import BaseModel


class EnsureStaticsAttributesSchemaResult(BaseModel):
    hp: int
    speed: int
    attack: int
    defense: int
    special_attack: int
    special_defense: int


class EnsureAttributesSchemaResult(BaseModel):
    hp: int
    speed: int
    height: int
    weight: int
    attack: int
    defense: int
    special_attack: int
    special_defense: int
    base_experience: int


class EnsureSpecieAttributesSchemaResult(BaseModel):
    habitat: Optional[str] = None
    is_baby: bool
    shape_name: Optional[str] = None
    shape_url: Optional[str] = None
    is_mythical: bool
    gender_rate: int
    is_legendary: bool
    capture_rate: int
    hatch_counter: int
    base_happiness: int
    evolution_chain_url: Optional[str] = None
    evolves_from_species: Optional[str] = None
    has_gender_differences: bool
