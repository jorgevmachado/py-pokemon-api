import logging

import pytest
import pytest_asyncio

from app.core.cache.manager import CacheManager
from app.core.cache.service import CacheService
from app.core.logging import LoggingParams
from app.shared.schemas import FilterPage


@pytest_asyncio.fixture
async def cache_service(redis_client):
    class TestableCacheService(CacheService):
        def __init__(self, logger_params, alias, prefix, redis_client):
            super().__init__(logger_params=logger_params)
            self.alias = alias
            self.prefix = prefix
            self.cache = CacheManager(redis_client=redis_client)

    return TestableCacheService(
        logger_params=LoggingParams(
            logger=logging.getLogger(__name__),
            service='cache_service',
            operation='test_cache',
        ),
        redis_client=redis_client,
        alias='test_cache',
        prefix='test_cache',
    )


class TestCacheServiceBuildKeyList:
    @staticmethod
    @pytest.mark.asyncio
    async def test_cache_service_build_key_list(cache_service):
        page_filter = FilterPage(offset=0, limit=10)
        key = cache_service.build_key_list(page_filter)
        assert key.startswith(f'{cache_service.prefix}:list')
