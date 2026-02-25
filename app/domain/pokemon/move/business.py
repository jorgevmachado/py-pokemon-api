from pydantic import BaseModel

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
