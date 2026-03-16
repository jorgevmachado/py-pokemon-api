from datetime import datetime
from typing import Any

from app.core.logging import LoggingParams, log_service_success
from app.core.settings import Settings
from app.domain.pokemon.business import PokemonBusiness
from app.domain.pokemon.model import Pokemon
from app.domain.pokemon.schema import PokemonSchema
from app.shared.cache import CacheService
from app.shared.exceptions import handle_service_exception


class PokemonCacheService(CacheService):
    def __init__(
        self,
        *,
        logger_params: LoggingParams,
    ):
        self.logger_params = logger_params
        self.business = PokemonBusiness()
        super().__init__(prefix='pokemon')

    def build_catalog_key(self) -> str:
        return self.build_key('catalog')

    async def cache_catalog(self, pokemons: list[Pokemon]) -> None:
        if not pokemons:
            return

        try:
            key = self.build_catalog_key()
            await self.set_json(
                key,
                value=self.business.serialize_catalog(pokemons),
                ttl_seconds=None,
            )
            log_service_success(
                self.logger_params,
                operation='cache_catalog',
                message='Pokemon catalog cached successfully',
            )
        except Exception as exception:
            handle_service_exception(
                exception,
                logger=self.logger_params.logger,
                service=self.logger_params.service,
                operation='cache_catalog',
                raise_exception=False,
            )

    async def cache_catalog_append(self, pokemons: list[Pokemon]) -> None:
        if not pokemons:
            return

        try:
            current_catalog = await self.get_catalog()
            catalog_map = {pokemon.name.lower(): pokemon for pokemon in current_catalog}

            for pokemon in pokemons:
                serialized = PokemonSchema.model_validate(pokemon)
                catalog_map[serialized.name.lower()] = serialized

            ordered_catalog = sorted(catalog_map.values(), key=lambda item: item.order)

            await self.set_json(
                key=self.build_catalog_key(),
                value=[pokemon.model_dump(mode='json') for pokemon in ordered_catalog],
                ttl_seconds=None,
            )
            log_service_success(
                self.logger_params,
                operation='cache_catalog_append',
                message='Pokemon catalog appended successfully',
            )
        except Exception as exception:
            handle_service_exception(
                exception,
                logger=self.logger_params.logger,
                service=self.logger_params.service,
                operation='cache_catalog_append',
                raise_exception=False,
            )

    async def get_catalog(self) -> list[PokemonSchema]:
        key = self.build_catalog_key()
        payload = await self.get_json(key)

        if not payload:
            return []

        return self.business.deserialize_catalog(payload)

    async def delete_catalog(self) -> None:
        key = self.build_catalog_key()
        await self.delete(key)

    def build_meta_key(self) -> str:
        return self.build_key('meta')

    async def cache_meta(self, *, db_total: int, external_total: int) -> bool:
        try:
            was_cached = await self.set_json(
                key=self.build_meta_key(),
                value={
                    'db_total': db_total,
                    'external_total': external_total,
                    'last_sync_at': datetime.now().isoformat(),
                },
                ttl_seconds=Settings().REDIS_POKEMON_SYNC_CHECK_SECONDS,
            )
            if not was_cached:
                return False

            log_service_success(
                self.logger_params,
                operation='cache_meta',
                message='Pokemon sync metadata cached successfully',
            )
            return True
        except Exception as exception:
            handle_service_exception(
                exception,
                logger=self.logger_params.logger,
                service=self.logger_params.service,
                operation='cache_meta',
                raise_exception=False,
            )
            return False

    async def get_meta(self) -> dict[str, Any] | None:
        key = self.build_meta_key()
        payload = await self.get_json(key)

        if not payload:
            return None
        return payload
