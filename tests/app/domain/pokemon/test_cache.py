import logging

import pytest

from app.core.logging import LoggingParams
from app.domain.pokemon.cache import PokemonCacheService


@pytest.fixture
def pokemon_cache_service(redis_client):
    return PokemonCacheService(
        logger_params=LoggingParams(
            logger=logging.getLogger(__name__),
            service='pokemon',
            operation='test_cache',
        )
    )


@pytest.mark.asyncio
async def test_build_catalog_key(pokemon_cache_service):
    assert pokemon_cache_service.build_catalog_key() == 'pokemon:catalog'


@pytest.mark.asyncio
async def test_get_catalog_returns_empty_list_when_cache_misses(pokemon_cache_service):
    result = await pokemon_cache_service.get_catalog()

    assert result == []


@pytest.mark.asyncio
async def test_get_catalog_returns_cached_catalog(pokemon_cache_service):
    payload = [
        {'name': 'bulbasaur', 'order': 1},
        {'name': 'ivysaur', 'order': 2},
    ]

    await pokemon_cache_service.set_json(
        key=pokemon_cache_service.build_catalog_key(),
        value=payload,
    )

    result = await pokemon_cache_service.get_catalog()

    assert result == payload


@pytest.mark.asyncio
async def test_build_meta_key(pokemon_cache_service):
    assert pokemon_cache_service.build_meta_key() == 'pokemon:meta'


@pytest.mark.asyncio
async def test_get_meta_returns_none_when_cache_misses(pokemon_cache_service):
    result = await pokemon_cache_service.get_meta()

    assert result is None


@pytest.mark.asyncio
async def test_get_meta_returns_cached_metadata(pokemon_cache_service):
    payload = {
        'db_total': 1302,
        'external_total': 1302,
        'last_sync_at': '2026-03-16T12:00:00',
    }

    await pokemon_cache_service.set_json(
        key=pokemon_cache_service.build_meta_key(),
        value=payload,
    )

    result = await pokemon_cache_service.get_meta()

    assert result == payload
