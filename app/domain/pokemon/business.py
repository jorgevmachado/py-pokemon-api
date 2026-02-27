from typing import Optional

from sqlalchemy import inspect

from app.domain.pokemon.external.schemas.evolution import (
    PokemonExternalEvolutionChainEvolvesToSchemaResponse,
    PokemonExternalEvolutionChainSchemaResponse,
)
from app.domain.pokemon.schema import PokemonSchema
from app.models import Pokemon


class PokemonBusiness:
    def ensure_evolution(
        self,
        params: Optional[PokemonExternalEvolutionChainSchemaResponse] = None,
    ) -> list[str]:
        if not params:
            return []

        return [
            params.species.name,
            *self.ensure_next_evolution(params.evolves_to),
        ]

    def ensure_next_evolution(
        self,
        params: Optional[list[PokemonExternalEvolutionChainEvolvesToSchemaResponse]] = None,
    ) -> list[str]:
        if not params:
            return []

        return [
            name
            for item in params
            for name in [
                item.species.name,
                *self.ensure_next_evolution(item.evolves_to),
            ]
        ]

    @staticmethod
    def merge_if_changed(
        pokemon_target: Pokemon,
        pokemon_source: PokemonSchema,
    ) -> Pokemon:
        mapper = inspect(Pokemon)

        for column in mapper.columns:
            key = column.key
            source_value = getattr(pokemon_source, key, None)

            if source_value is not None:
                current_value = getattr(pokemon_target, key)
                if current_value != source_value:
                    setattr(pokemon_target, key, source_value)
        return pokemon_target
