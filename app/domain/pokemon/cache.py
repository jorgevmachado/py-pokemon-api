from typing import Annotated

from fastapi import Query
from fastapi_pagination import LimitOffsetPage

from app.core.cache.manager import CacheManager
from app.core.logging import LoggingParams, log_service_success
from app.domain.pokemon.business import PokemonBusiness
from app.domain.pokemon.schema import PokemonFilterPage, PokemonSchema


class PokemonCacheService:
    def __init__(
        self,
        *,
        logger_params: LoggingParams,
    ):
        self.logger_params = logger_params
        self.business = PokemonBusiness()
        self.prefix = 'pokemon'
        self.cache = CacheManager()

    def build_key_all(self, page_filter: Annotated[PokemonFilterPage, Query()] = None):
        log_service_success(
            self.logger_params,
            operation='cache_build_key_all',
            message='The Pokémon list cache key was successfully created.',
        )
        return self.cache.build_key(self.prefix, 'list', page_filter.model_dump())

    async def get_all(
        self, key: str
    ) -> list[PokemonSchema] | LimitOffsetPage[PokemonSchema] | None:
        cached = await self.cache.get_cache(key)

        if cached and 'type' in cached and cached['type'] == 'list':
            list_pokemons_deserialized: list[PokemonSchema] = []
            for pokemon in cached['data']:
                if not isinstance(pokemon, dict):
                    continue
                list_pokemons_deserialized.append(PokemonSchema.model_validate(pokemon))
            log_service_success(
                self.logger_params,
                operation='cache_get_all',
                message='List of Pokémon stored in cache.',
            )
            return list_pokemons_deserialized

        if cached and 'type' in cached and cached['type'] == 'paginate':
            log_service_success(
                self.logger_params,
                operation='cache_get_all',
                message='Paginated list of cached Pokémon',
            )
            return LimitOffsetPage[PokemonSchema].model_validate(cached['data'])

        log_service_success(
            self.logger_params,
            operation='cache_get_all',
            message=' No Pokémon data is cached.',
        )

        return None

    async def set_all(
        self, key: str, data: list[PokemonSchema] | LimitOffsetPage[PokemonSchema]
    ) -> None:
        if isinstance(data, list):
            list_pokemons_serialized = [
                PokemonSchema.model_validate(pokemon).serialize() for pokemon in data
            ]
            await self.cache.set_cache(key, {'type': 'list', 'data': list_pokemons_serialized})
            log_service_success(
                self.logger_params,
                operation='cache_set_all',
                message='List of Pokémon successfully cached.',
            )
            return None
        if isinstance(data, LimitOffsetPage):
            pokemons_serialized = (
                LimitOffsetPage[PokemonSchema].model_validate(data).model_dump(mode='json')
            )
            await self.cache.set_cache(key, {'type': 'paginate', 'data': pokemons_serialized})
            log_service_success(
                self.logger_params,
                operation='cache_set_all',
                message='Paginated list of Pokémon successfully cached.',
            )
            return None

        log_service_success(
            self.logger_params,
            operation='cache_set_all',
            message='No Pokémon data was cached..',
        )
        return None

    def build_key_meta(self):
        log_service_success(
            self.logger_params,
            operation='cache_build_key_meta',
            message='The Pokémon metadata cache key was successfully created.',
        )
        return self.cache.build_key(self.prefix, 'meta')

    async def get_meta(self) -> dict | None:
        log_service_success(
            self.logger_params,
            operation='cache_get_meta',
            message='Cached Pokémon metadata.',
        )
        return await self.cache.get_cache(self.build_key_meta())

    async def set_meta(self, db_total: int, external_total: int) -> None:
        log_service_success(
            self.logger_params,
            operation='cache_set_meta',
            message='Pokémon metadata successfully cached.',
        )
        await self.cache.set_cache(
            self.build_key_meta(), {'db_total': db_total, 'external_total': external_total}
        )

    def build_key_one(self, name: str):
        log_service_success(
            self.logger_params,
            operation='cache_build_key_one',
            message='The Pokémon cache key was successfully created.',
        )
        return self.cache.build_key(self.prefix,  name)

    async def set_one(self, key: str, pokemon: PokemonSchema) -> None:
        pokemon_serialized = PokemonSchema.model_validate(pokemon).serialize()
        await self.cache.set_cache(key, pokemon_serialized)
        log_service_success(
            self.logger_params,
            operation='cache_set_one',
            message='Pokémon successfully cached.',
        )
        return None

    async def get_one(self, key: str) -> PokemonSchema | None:
        cached = await self.cache.get_cache(key)
        if cached:
            log_service_success(
                self.logger_params,
                operation='cache_get_one',
                message=f'Pokémon {key} stored in cache',
            )
            return PokemonSchema.model_validate(cached)
        log_service_success(
            self.logger_params,
            operation='cache_get_one',
            message=f'No Pokémon {key} is cached.',
        )
        return None