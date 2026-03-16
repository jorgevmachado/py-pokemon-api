from typing import Any

from app.core.logging import LoggingParams
from app.shared.cache import CacheService


class PokemonCacheService(CacheService):
    def __init__(
        self,
        *,
        logger_params: LoggingParams,
    ):
        self.logger_params = logger_params
        super().__init__(prefix='pokemon')

    def build_catalog_key(self) -> str:
        return self.build_key('catalog')

    async def get_catalog(self) -> list[dict]:
        key = self.build_catalog_key()
        payload = await self.get_json(key)

        if not payload:
            return []

        return payload

    def build_meta_key(self) -> str:
        return self.build_key('meta')

    async def get_meta(self) -> dict[str, Any] | None:
        key = self.build_meta_key()
        payload = await self.get_json(key)

        if not payload:
            return None
        return payload
