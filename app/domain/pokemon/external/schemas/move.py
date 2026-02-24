from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.domain.pokemon.external.schemas import (
    PokemonExternalBase,
    PokemonExternalLanguage,
)


class PokemonExternalMoveContestCombosSchemaResponse(BaseModel):
    model_config = ConfigDict(extra='ignore')
    normal: dict[str, list[PokemonExternalBase] | None]
    super: dict[str, list[PokemonExternalBase] | None]


class PokemonExternalMoveContestEffectSchemaResponse(BaseModel):
    model_config = ConfigDict(extra='ignore')
    url: str


class PokemonExternalMoveEffectEntriesSchemaResponse(BaseModel):
    model_config = ConfigDict(extra='ignore')
    effect: str
    language: PokemonExternalLanguage
    short_effect: str


class PokemonExternalMoveFlavorTextEntriesSchemaResponse(BaseModel):
    model_config = ConfigDict(extra='ignore')
    flavor_text: str
    language: PokemonExternalLanguage
    version_group: dict[str, str]


class PokemonExternalMoveMachineSchemaResponse(BaseModel):
    model_config = ConfigDict(extra='ignore')
    machine: dict[str, str]
    version_group: dict[str, str]


class PokemonExternalMoveMetaSchemaResponse(BaseModel):
    model_config = ConfigDict(extra='ignore')
    ailment: PokemonExternalBase
    ailment_chance: int
    category: PokemonExternalBase
    crit_rate: int
    drain: int
    flinch_chance: int
    healing: int
    max_hits: Optional[int] = None
    max_turns: Optional[int] = None
    min_hits: Optional[int] = None
    min_turns: Optional[int] = None
    stat_chance: int


class PokemonExternalMoveNamesSchemaResponse(BaseModel):
    model_config = ConfigDict(extra='ignore')
    language: PokemonExternalLanguage
    name: str


class PokemonExternalMoveSchemaResponse(BaseModel):
    model_config = ConfigDict(extra='ignore')
    accuracy: int
    contest_combos: PokemonExternalMoveContestCombosSchemaResponse
    contest_effect: PokemonExternalMoveContestEffectSchemaResponse
    contest_type: PokemonExternalBase
    damage_class: PokemonExternalBase
    effect_chance: Optional[PokemonExternalBase] = None
    effect_changes: list[dict]
    effect_entries: list[PokemonExternalMoveEffectEntriesSchemaResponse]
    flavor_text_entries: list[PokemonExternalMoveFlavorTextEntriesSchemaResponse]
    generation: PokemonExternalBase
    id: int
    learned_by_pokemon: list[PokemonExternalBase]
    machines: list[PokemonExternalMoveMachineSchemaResponse]
    meta: PokemonExternalMoveMetaSchemaResponse
    name: str
    names: list[PokemonExternalMoveNamesSchemaResponse]
    past_values: list[str]
    power: int
    pp: int
    priority: int
    stat_changes: list[str]
    super_contest_effect: PokemonExternalMoveContestEffectSchemaResponse
    target: PokemonExternalBase
    type: PokemonExternalBase
