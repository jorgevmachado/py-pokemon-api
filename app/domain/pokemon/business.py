from typing import Optional

from fastapi_pagination import LimitOffsetPage, LimitOffsetParams
from sqlalchemy import inspect

from app.core.pagination import is_paginate, limit_paginate
from app.domain.pokemon.external.schemas.evolution import (
    PokemonExternalEvolutionChainEvolvesToSchemaResponse,
    PokemonExternalEvolutionChainSchemaResponse,
)
from app.domain.pokemon.schema import PokemonFilterPage, PokemonSchema
from app.models.pokemon import Pokemon
from app.shared.enums.status_enum import StatusEnum


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

    @staticmethod
    def find_first_pokemon(
        pokemons: list[Pokemon],
        pokemon_name: str | None = None,
    ) -> Optional[Pokemon]:
        if not pokemons:
            return None

        if not pokemon_name:
            return PokemonBusiness.get_random_pokemon(pokemons=pokemons)

        return next(
            (p for p in pokemons if p.name == pokemon_name),
            None,
        )

    @staticmethod
    def get_random_pokemon(
        pokemons: list[Pokemon], complete: Optional[bool] = True
    ) -> Optional[Pokemon]:
        if not pokemons:
            return None

        pokemon_complete = next(
            (p for p in pokemons if p.status == StatusEnum.COMPLETE),
            None,
        )
        if complete and pokemon_complete:
            return pokemon_complete

        orders = [p.order for p in pokemons]
        random_order = orders[int(__import__('random').random() * len(orders))]
        return next(
            (p for p in pokemons if p.order == random_order),
            None,
        )

    @staticmethod
    def serialize_catalog(pokemons: list[Pokemon]) -> list[dict]:
        return [
            PokemonSchema.model_validate(pokemon).model_dump(mode='json')
            for pokemon in pokemons
        ]

    @staticmethod
    def deserialize_catalog(payload: list[dict]) -> list[PokemonSchema]:
        result = []
        for item in payload:
            if not isinstance(item, dict):
                continue
            result.append(PokemonSchema.model_validate(item))
        return result

    @staticmethod
    def filter_and_paginate_catalog(
        catalog: list[PokemonSchema],
        page_filter: Optional[PokemonFilterPage] = None,
    ) -> LimitOffsetPage[PokemonSchema] | list[PokemonSchema]:

        raw_filters = page_filter.model_dump(exclude_none=True) if page_filter else {}

        raw_filters.pop('offset', None)
        raw_filters.pop('limit', None)

        valid_fields = set(PokemonSchema.model_fields.keys())
        filters = {k: v for k, v in raw_filters.items() if k in valid_fields and v is not None}

        filtered_catalog = [
            pokemon for pokemon in catalog if PokemonBusiness._matches_filter(pokemon, filters)
        ]

        if is_paginate(page_filter):
            params = LimitOffsetParams(
                limit=limit_paginate(page_filter.limit),
                offset=page_filter.offset,
            )
            start = params.offset
            end = start + params.limit
            return LimitOffsetPage.create(
                items=filtered_catalog[start:end],
                total=len(filtered_catalog),
                params=params,
            )
        return filtered_catalog

    @staticmethod
    def _matches_filter(
        pokemon: PokemonSchema,
        filters: dict[str, object],
    ) -> bool:
        if not filters:
            return True

        for key, value in filters.items():
            pokemon_value = getattr(pokemon, key, None)

            if isinstance(pokemon_value, str) and isinstance(value, str):
                if pokemon_value.lower() != value.lower():
                    return False
                continue

            if pokemon_value != value:
                return False
        return True
