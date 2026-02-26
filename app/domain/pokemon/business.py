from typing import Optional

from app.domain.pokemon.external.schemas.evolution import (
    PokemonExternalEvolutionChainEvolvesToSchemaResponse,
    PokemonExternalEvolutionChainSchemaResponse,
)


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
