import random
from typing import Sequence

from pydantic import BaseModel

from app.domain.move.model import PokemonMove
from app.domain.pokemon.external.schemas import (
    PokemonExternalMoveEffectEntriesSchemaResponse,
)


class EffectEntry(BaseModel):
    effect: str
    short_effect: str


class PokemonMoveBusiness:
    @staticmethod
    def ensure_effect_message(
        effect_entries: list[PokemonExternalMoveEffectEntriesSchemaResponse],
    ) -> EffectEntry:
        effect_entry = next(
            (entry for entry in effect_entries if entry.language.name == 'en'),
            effect_entries[0] if effect_entries else None,
        )
        effect = effect_entry.effect if effect_entry else ''
        short_effect = effect_entry.short_effect if effect_entry else ''
        return EffectEntry(effect=effect, short_effect=short_effect)

    @staticmethod
    def select_random_moves(
        available_moves: Sequence[PokemonMove],
        max_moves: int = 4,
    ) -> list[PokemonMove]:
        if not available_moves:
            return []

        moves_count = len(available_moves)
        if moves_count <= max_moves:
            return list(available_moves)

        return random.sample(list(available_moves), max_moves)
