import json
import logging
from typing import Any

from redis.exceptions import RedisError

from app.core.redis import redis_client
from app.core.settings import Settings

logger = logging.getLogger(__name__)


class CacheService:
    def __init__(
        self,
        *,
        prefix: str,
        ttl_seconds: int | None = None,
    ):
        self.redis = redis_client
        self.prefix = prefix
        self.ttl_seconds = (
            ttl_seconds if ttl_seconds is not None else Settings().REDIS_CACHE_TTL_SECONDS
        )

    def build_key(self, *parts: str) -> str:
        normalized_parts = [part.strip().lower() for part in parts if part and part.strip()]
        if not normalized_parts:
            return self.prefix
        return f'{self.prefix}:{":".join(normalized_parts)}'

    async def set_json(
        self,
        key: str,
        value: Any,
        *,
        ttl_seconds: int | None = None,
    ) -> None:
        try:
            payload = json.dumps(value, default=str)
            expires_in = self.ttl_seconds if ttl_seconds is None else ttl_seconds

            if expires_in and expires_in > 0:
                await self.redis.set(key, payload, ex=expires_in)
                return

            await self.redis.set(key, payload)
        except RedisError:
            logger.warning('Redis unavailable while setting key: %s', key)

    async def get_json(self, key: str) -> Any | None:
        try:
            value = await self.redis.get(key)
            if value is None:
                return None
            return json.loads(value)
        except RedisError:
            logger.warning('Redis unavailable while reading key: %s', key)
            return None

    async def delete(self, key: str) -> None:
        try:
            await self.redis.delete(key)
        except RedisError:
            logger.warning('Redis unavailable while deleting key: %s', key)

    async def set_many_json(
        self,
        key_values: dict[str, Any],
        *,
        ttl_seconds: int | None = None,
    ) -> None:
        if not key_values:
            return

        try:
            expires_in = self.ttl_seconds if ttl_seconds is None else ttl_seconds

            async with self.redis.pipeline(transaction=False) as pipe:
                for key, value in key_values.items():
                    payload = json.dumps(value, default=str)
                    if expires_in and expires_in > 0:
                        pipe.set(key, payload, ex=expires_in)
                    else:
                        pipe.set(key, payload)

                await pipe.execute()
        except RedisError:
            logger.warning('Redis unavailable while writing %d keys', len(key_values))
