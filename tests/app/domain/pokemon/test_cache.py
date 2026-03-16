import asyncio
import logging
from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest

from app.core.logging import LoggingParams
from app.domain.pokemon.cache import PokemonCacheService
from app.shared.enums.status_enum import StatusEnum

INFINITE_TTL = 0
META_TTL_24H = 86400
ARG_INDEX_TWO = 2


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
    now = datetime.now().isoformat()
    payload = [
        {
            'id': '1',
            'url': 'https://pokeapi.co/api/v2/pokemon/1/',
            'name': 'bulbasaur',
            'order': 1,
            'status': StatusEnum.COMPLETE.value,
            'external_image': 'https://img.pokemondb.net/artwork/bulbasaur.jpg',
            'created_at': now,
            'updated_at': now,
        },
        {
            'id': '2',
            'url': 'https://pokeapi.co/api/v2/pokemon/2/',
            'name': 'ivysaur',
            'order': 2,
            'status': StatusEnum.COMPLETE.value,
            'external_image': 'https://img.pokemondb.net/artwork/ivysaur.jpg',
            'created_at': now,
            'updated_at': now,
        },
    ]

    await pokemon_cache_service.set_json(
        key=pokemon_cache_service.build_catalog_key(),
        value=payload,
    )

    result = await pokemon_cache_service.get_catalog()

    # Compare only the fields present in the payload for each result
    for i, poke in enumerate(payload):
        for key in poke:
            value = getattr(result[i], key)
            if key in {'created_at', 'updated_at'}:
                assert value.isoformat() == poke[key]
            else:
                assert value == poke[key]


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


@pytest.mark.asyncio
async def test_cache_catalog_sets_ttl_zero(pokemon_cache_service):
    pokemons = [
        type('Pokemon', (), {'name': 'bulbasaur', 'order': 1})(),
        type('Pokemon', (), {'name': 'ivysaur', 'order': 2})(),
    ]
    with patch.object(
        pokemon_cache_service, 'set_json', new_callable=AsyncMock
    ) as mock_set_json:
        with patch.object(
            pokemon_cache_service.business,
            'serialize_catalog',
            return_value=[{'name': 'bulbasaur'}, {'name': 'ivysaur'}],
        ):
            await pokemon_cache_service.cache_catalog(pokemons)
        mock_set_json.assert_awaited_once()
        args, kwargs = mock_set_json.call_args
        ttl = kwargs.get(
            'ttl_seconds',
            args[ARG_INDEX_TWO] if len(args) > ARG_INDEX_TWO else None,
        )
        assert ttl in {INFINITE_TTL, None}


@pytest.mark.asyncio
async def test_cache_meta_sets_ttl_24h(pokemon_cache_service):
    with patch.object(
        pokemon_cache_service, 'set_json', new_callable=AsyncMock
    ) as mock_set_json:
        with patch('app.domain.pokemon.cache.Settings') as mock_settings:
            mock_settings.return_value.REDIS_POKEMON_SYNC_CHECK_SECONDS = META_TTL_24H
            await pokemon_cache_service.cache_meta(db_total=10, external_total=20)
        mock_set_json.assert_awaited_once()
        args, kwargs = mock_set_json.call_args
        ttl = kwargs.get(
            'ttl_seconds',
            args[ARG_INDEX_TWO] if len(args) > ARG_INDEX_TWO else None,
        )
        assert ttl == META_TTL_24H


@pytest.mark.asyncio
async def test_cache_catalog_handles_exception(pokemon_cache_service):
    now = datetime.now().isoformat()
    pokemons = [
        type(
            'Pokemon',
            (),
            {
                'id': '1',
                'name': 'bulbasaur',
                'order': 1,
                'url': 'https://pokeapi.co/api/v2/pokemon/1/',
                'status': StatusEnum.COMPLETE.value,
                'external_image': 'https://img.pokemondb.net/artwork/bulbasaur.jpg',
                'created_at': now,
                'updated_at': now,
            },
        )()
    ]
    with patch.object(
        pokemon_cache_service, 'set_json', side_effect=Exception('fail')
    ) as mock_set_json:
        await pokemon_cache_service.cache_catalog(pokemons)
        mock_set_json.assert_called_once()


@pytest.mark.asyncio
async def test_cache_catalog_append_handles_exception(pokemon_cache_service):
    pokemons = [type('Pokemon', (), {'name': 'bulbasaur', 'order': 1})()]
    with patch.object(
        pokemon_cache_service, 'get_catalog', side_effect=Exception('fail')
    ) as mock_get_catalog:
        await pokemon_cache_service.cache_catalog_append(pokemons)
        mock_get_catalog.assert_called_once()


@pytest.mark.asyncio
async def test_cache_meta_returns_false_on_exception(pokemon_cache_service):
    with patch.object(pokemon_cache_service, 'set_json', side_effect=Exception('fail')):
        result = await pokemon_cache_service.cache_meta(db_total=1, external_total=2)
        assert result is False


@pytest.mark.asyncio
async def test_cache_meta_returns_false_when_not_cached(pokemon_cache_service):
    with patch.object(pokemon_cache_service, 'set_json', return_value=False):
        result = await pokemon_cache_service.cache_meta(db_total=1, external_total=2)
        assert result is False


@pytest.mark.asyncio
async def test_delete_catalog_calls_delete(pokemon_cache_service):
    with patch.object(pokemon_cache_service, 'delete', new_callable=AsyncMock) as mock_delete:
        await pokemon_cache_service.delete_catalog()
        mock_delete.assert_awaited_once_with(pokemon_cache_service.build_catalog_key())


@pytest.mark.asyncio
def test_cache_catalog_returns_early_on_empty_list(pokemon_cache_service):
    with patch.object(
        pokemon_cache_service, 'set_json', new_callable=AsyncMock
    ) as mock_set_json:
        asyncio.run(pokemon_cache_service.cache_catalog([]))
        mock_set_json.assert_not_called()


@pytest.mark.asyncio
def test_cache_catalog_append_returns_early_on_empty_list(pokemon_cache_service):
    with patch.object(
        pokemon_cache_service, 'get_catalog', new_callable=AsyncMock
    ) as mock_get_catalog:
        asyncio.run(pokemon_cache_service.cache_catalog_append([]))
        mock_get_catalog.assert_not_called()


@pytest.mark.asyncio
def test_cache_catalog_append_handles_serialization_exception(pokemon_cache_service):
    pokemons = [type('Pokemon', (), {'name': 'bulbasaur', 'order': 1})()]
    with patch.object(
        pokemon_cache_service, 'get_catalog', new_callable=AsyncMock
    ) as mock_get_catalog:
        mock_get_catalog.return_value = []
        with patch(
            'app.domain.pokemon.cache.PokemonSchema.model_validate',
            side_effect=Exception('fail'),
        ):
            with patch('app.domain.pokemon.cache.handle_service_exception') as mock_handle:
                asyncio.run(pokemon_cache_service.cache_catalog_append(pokemons))
                mock_handle.assert_called_once()


@pytest.mark.asyncio
def test_cache_catalog_append_handles_set_json_exception(pokemon_cache_service):
    pokemons = [type('Pokemon', (), {'name': 'bulbasaur', 'order': 1})()]
    with patch.object(
        pokemon_cache_service, 'get_catalog', new_callable=AsyncMock
    ) as mock_get_catalog:
        mock_get_catalog.return_value = []
        with patch(
            'app.domain.pokemon.cache.PokemonSchema.model_validate',
            return_value=type(
                'PokemonSchema',
                (),
                {
                    'name': 'bulbasaur',
                    'order': 1,
                    'model_dump': lambda self, mode: {'name': 'bulbasaur', 'order': 1},
                },
            )(),
        ):
            with patch.object(
                pokemon_cache_service, 'set_json', side_effect=Exception('fail')
            ):
                with patch('app.domain.pokemon.cache.handle_service_exception') as mock_handle:
                    asyncio.run(pokemon_cache_service.cache_catalog_append(pokemons))
                    mock_handle.assert_called_once()


@pytest.mark.asyncio
def test_cache_catalog_append_calls_log_service_success(pokemon_cache_service):
    pokemons = [type('Pokemon', (), {'name': 'bulbasaur', 'order': 1})()]
    with patch.object(
        pokemon_cache_service, 'get_catalog', new_callable=AsyncMock
    ) as mock_get_catalog:
        mock_get_catalog.return_value = []
        with patch(
            'app.domain.pokemon.cache.PokemonSchema.model_validate',
            return_value=type(
                'PokemonSchema',
                (),
                {
                    'name': 'bulbasaur',
                    'order': 1,
                    'model_dump': lambda self, mode: {'name': 'bulbasaur', 'order': 1},
                },
            )(),
        ):
            with patch.object(pokemon_cache_service, 'set_json', new_callable=AsyncMock):
                with patch('app.domain.pokemon.cache.log_service_success') as mock_log:
                    asyncio.run(pokemon_cache_service.cache_catalog_append(pokemons))
                    mock_log.assert_called_once_with(
                        pokemon_cache_service.logger_params,
                        operation='cache_catalog_append',
                        message='Pokemon catalog appended successfully',
                    )
