import logging
from datetime import datetime
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from fastapi_pagination import LimitOffsetPage

from app.core.cache.manager import CacheManager
from app.core.logging import LoggingParams
from app.domain.pokemon.cache import PokemonCacheService
from app.domain.pokemon.schema import PokemonFilterPage, PokemonSchema
from app.shared.enums.status_enum import StatusEnum

# Remove unused imports

INFINITE_TTL = 0
META_TTL_24H = 86400
ARG_INDEX_TWO = 2

POKEMON_LIST_LENGTH = 2
POKEMON_DB_TOTAL = 1302
POKEMON_EXTERNAL_TOTAL = 1302


@pytest_asyncio.fixture
async def pokemon_cache_service(redis_client):
    class TestablePokemonCacheService(PokemonCacheService):
        def __init__(self, logger_params, redis_client):
            super().__init__(logger_params=logger_params)
            self.cache = CacheManager(redis_client=redis_client)

    return TestablePokemonCacheService(
        logger_params=LoggingParams(
            logger=logging.getLogger(__name__),
            service='pokemon',
            operation='test_cache',
        ),
        redis_client=redis_client,
    )


class TestPokemonCacheServiceBuildKeyAll:
    @staticmethod
    @pytest.mark.asyncio
    async def test_build_key_all(pokemon_cache_service):
        page_filter = PokemonFilterPage(offset=0, limit=10)
        key = pokemon_cache_service.build_key_all(page_filter)
        assert key.startswith('pokemon:list')


class TestPokemonCacheServiceGetAll:
    @staticmethod
    @pytest.mark.asyncio
    async def test_get_all_returns_none_when_cache_misses(pokemon_cache_service):
        page_filter = PokemonFilterPage(offset=0, limit=10)
        key = pokemon_cache_service.build_key_all(page_filter)
        result = await pokemon_cache_service.get_all(key)
        assert result is None

    @staticmethod
    @pytest.mark.asyncio
    async def test_set_and_get_all(pokemon_cache_service):
        now = datetime.now()
        pokemons = [
            PokemonSchema(
                id='1',
                url='https://pokeapi.co/api/v2/pokemon/1/',
                name='bulbasaur',
                order=1,
                status=StatusEnum.COMPLETE,
                external_image='https://img.pokemondb.net/artwork/bulbasaur.jpg',
                created_at=now,
                updated_at=now,
            ),
            PokemonSchema(
                id='2',
                url='https://pokeapi.co/api/v2/pokemon/2/',
                name='ivysaur',
                order=2,
                status=StatusEnum.COMPLETE,
                external_image='https://img.pokemondb.net/artwork/ivysaur.jpg',
                created_at=now,
                updated_at=now,
            ),
        ]
        page_filter = PokemonFilterPage(offset=0, limit=10)
        key = pokemon_cache_service.build_key_all(page_filter)
        await pokemon_cache_service.set_all(key, pokemons)
        result = await pokemon_cache_service.get_all(key)
        assert isinstance(result, list)
        assert len(result) == POKEMON_LIST_LENGTH
        assert result[0].name == 'bulbasaur'
        assert result[1].name == 'ivysaur'

    @staticmethod
    @pytest.mark.asyncio
    async def test_get_all_skips_non_dict_entries(pokemon_cache_service):
        key = 'pokemon:list:test'
        cached_data = {
            'type': 'list',
            'data': [
                {
                    'id': '1',
                    'name': 'bulbasaur',
                    'url': '',
                    'order': 1,
                    'status': StatusEnum.COMPLETE,
                    'external_image': '',
                    'created_at': datetime.now(),
                    'updated_at': datetime.now(),
                },
                'not_a_dict',
                {
                    'id': '2',
                    'name': 'ivysaur',
                    'url': '',
                    'order': 2,
                    'status': StatusEnum.COMPLETE,
                    'external_image': '',
                    'created_at': datetime.now(),
                    'updated_at': datetime.now(),
                },
            ],
        }
        pokemon_cache_service.cache.get_cache = AsyncMock(return_value=cached_data)
        result = await pokemon_cache_service.get_all(key)
        assert isinstance(result, list)
        assert len(result) == POKEMON_LIST_LENGTH
        assert all(isinstance(p, PokemonSchema) for p in result)

    @staticmethod
    @pytest.mark.asyncio
    async def test_get_all_paginate_type(pokemon_cache_service):
        key = 'pokemon:list:paginate'
        page_obj = LimitOffsetPage[PokemonSchema](
            items=[
                PokemonSchema(
                    id='1',
                    url='',
                    name='bulbasaur',
                    order=1,
                    status=StatusEnum.COMPLETE,
                    external_image='',
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                )
            ],
            limit=10,
            offset=0,
            total=1,
        )
        cached_data = {'type': 'paginate', 'data': page_obj.model_dump(mode='json')}
        pokemon_cache_service.cache.get_cache = AsyncMock(return_value=cached_data)
        result = await pokemon_cache_service.get_all(key)
        assert isinstance(result, LimitOffsetPage)
        assert result.total == 1
        assert result.items[0].name == 'bulbasaur'


class TestPokemonCacheServiceSetAll:
    @staticmethod
    @pytest.mark.asyncio
    async def test_set_all_with_paginate(pokemon_cache_service):
        key = 'pokemon:list:paginate'
        page_obj = LimitOffsetPage[PokemonSchema](
            items=[
                PokemonSchema(
                    id='1',
                    url='',
                    name='bulbasaur',
                    order=1,
                    status=StatusEnum.COMPLETE,
                    external_image='',
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                )
            ],
            limit=10,
            offset=0,
            total=1,
        )
        pokemon_cache_service.cache.set_cache = AsyncMock(return_value=None)
        result = await pokemon_cache_service.set_all(key, page_obj)
        assert result is None

    @staticmethod
    @pytest.mark.asyncio
    async def test_set_all_with_invalid_type(pokemon_cache_service):
        key = 'pokemon:list:invalid'
        invalid_data = object()
        pokemon_cache_service.cache.set_cache = AsyncMock(return_value=None)
        result = await pokemon_cache_service.set_all(key, invalid_data)
        assert result is None


class TestPokemonCacheServiceBuildKeyMeta:
    @staticmethod
    @pytest.mark.asyncio
    async def test_build_key_meta(pokemon_cache_service):
        key = pokemon_cache_service.build_key_meta()
        assert key == 'pokemon:meta'


class TestPokemonCacheServiceGetMeta:
    @staticmethod
    @pytest.mark.asyncio
    async def test_get_meta_returns_none_when_cache_misses(pokemon_cache_service):
        pokemon_cache_service.cache.get_cache = AsyncMock(return_value=None)
        result = await pokemon_cache_service.get_meta()
        assert result is None

    @staticmethod
    @pytest.mark.asyncio
    async def test_set_and_get_meta(pokemon_cache_service):
        await pokemon_cache_service.set_meta(
            db_total=POKEMON_DB_TOTAL, external_total=POKEMON_EXTERNAL_TOTAL
        )
        result = await pokemon_cache_service.get_meta()
        assert result['db_total'] == POKEMON_DB_TOTAL
        assert result['external_total'] == POKEMON_EXTERNAL_TOTAL


class TestPokemonCacheServiceBuildKeyOne:
    @staticmethod
    @pytest.mark.asyncio
    async def test_build_key_one(pokemon_cache_service):
        key = pokemon_cache_service.build_key_one('pikachu')
        assert key == 'pokemon:pikachu'


class TestPokemonCacheServiceSetOne:
    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_cache_service_set_one(pokemon_cache_service):
        pokemon = PokemonSchema(
            id='1',
            url='https://pokeapi.co/api/v2/pokemon/1/',
            name='bulbasaur',
            order=1,
            status=StatusEnum.COMPLETE,
            external_image='https://img.pokemondb.net/artwork/bulbasaur.jpg',
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        key = 'pokemon:pikachu'
        pokemon_cache_service.cache.set_cache = AsyncMock(return_value=None)
        result = await pokemon_cache_service.set_one(key, pokemon)
        assert result is None

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_cache_service_set_one_when_not_received_data(pokemon_cache_service):
        key = 'pokemon:pikachu'
        pokemon_cache_service.cache.set_cache = AsyncMock(return_value=None)
        result = await pokemon_cache_service.set_one(key, None)
        assert result is None


class TestPokemonCacheServiceGetOne:
    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_cache_service_get_one_returns_none_when_cache_misses(
        pokemon_cache_service,
    ):
        key = 'pokemon:pikachu'
        result = await pokemon_cache_service.get_one(key)
        assert result is None

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_cache_service_get_one_returns_pokemon(pokemon_cache_service):
        pokemon = PokemonSchema(
            id='1',
            url='https://pokeapi.co/api/v2/pokemon/1/',
            name='bulbasaur',
            order=1,
            status=StatusEnum.COMPLETE,
            external_image='https://img.pokemondb.net/artwork/bulbasaur.jpg',
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        key = 'pokemon:bulbasaur'
        await pokemon_cache_service.set_one(key, pokemon)
        result = await pokemon_cache_service.get_one(key)
        assert isinstance(result, PokemonSchema)
