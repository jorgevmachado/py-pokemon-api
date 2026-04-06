from datetime import datetime
from http import HTTPStatus
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.domain.pokemon.schema import PokemonFilterPage
from app.models.pokemon import Pokemon
from app.shared.enums.status_enum import StatusEnum
from tests.app.domain.pokemon.mock import (
    MOCK_ENTITY_ORDER,
    MOCK_POKEMON_ABILITIES_LIST,
    MOCK_POKEMON_GROWTH_RATE,
    MOCK_POKEMON_MOVE_LIST,
    MOCK_POKEMON_TYPES_LIST,
    MOCK_RELATIONSHIPS,
)


class TestPokemonServiceTotal:
    """Test scope for total method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_service_total_success(pokemon, pokemon_service):
        """Should return total pokemon count when query is successful"""
        result = await pokemon_service.total()
        assert result == 1


class TestPokemonServiceListSync:
    """Test scope for list_sync method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_service_list_sync_with_cached(pokemon, pokemon_service):
        pokemon_service.pokemon_cache_service.get_meta = AsyncMock(
            return_value='{"db_total": 1351, "external_total": 1350}'
        )
        result = await pokemon_service.list_sync()
        assert not result

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_service_list_sync_not_cached_total_0(pokemon, pokemon_service):
        with patch(
            'app.core.cache.manager.CacheManager.set_cache', new_callable=AsyncMock
        ) as mock_set_cache:
            mock_set_cache.return_value = None
            pokemon_service.pokemon_cache_service.get_meta = AsyncMock(return_value=None)
            pokemon_service.repository.total = AsyncMock(return_value=0)
            pokemon_service.external_service.pokemon_external_total = AsyncMock(
                return_value=1350
            )
            pokemon_service.initialize_database = AsyncMock(return_value=[pokemon])
            result = await pokemon_service.list_sync()
            assert result

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_service_list_sync_not_cached_total_different_external_total(
        pokemon, pokemon_service
    ):
        # Injeta o mock diretamente na instância do cache manager
        mock_redis_client = AsyncMock()
        mock_redis_client.setex.return_value = None
        pokemon_service.pokemon_cache_service.cache.redis_client = mock_redis_client
        pokemon_service.pokemon_cache_service.get_meta = AsyncMock(return_value=None)
        pokemon_service.repository.total = AsyncMock(return_value=1349)
        pokemon_service.external_service.pokemon_external_total = AsyncMock(return_value=1350)
        pokemon_service.initialize_database = AsyncMock(return_value=[pokemon])
        result = await pokemon_service.list_sync()
        assert result

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_service_list_sync_not_cached_and_not_different(
        pokemon, pokemon_service
    ):
        mock_redis_client = AsyncMock()
        mock_redis_client.setex.return_value = None
        pokemon_service.pokemon_cache_service.cache.redis_client = mock_redis_client
        pokemon_service.pokemon_cache_service.get_meta = AsyncMock(return_value=None)
        pokemon_service.repository.total = AsyncMock(return_value=1350)
        pokemon_service.external_service.pokemon_external_total = AsyncMock(return_value=1350)
        pokemon_service.initialize_database = AsyncMock(return_value=[pokemon])
        result = await pokemon_service.list_sync()
        assert not result


class TestPokemonServiceList:
    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_service_list_success(pokemon, pokemon_service):
        """Should return list of pokemon when query is successful"""
        pokemon_service.list_sync = AsyncMock(return_value=False)
        pokemon_service.repository.list_all = AsyncMock(return_value=[pokemon])

        result = await pokemon_service.list_all()
        assert isinstance(result, list)
        assert len(result) == 1

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_service_list_raises_exception(pokemon, pokemon_service):
        pokemon_service.list_sync = AsyncMock(return_value=False)
        pokemon_service.repository.list_all = AsyncMock(side_effect=Exception('boom'))

        page_filter = PokemonFilterPage(offset=0, limit=3)
        result = await pokemon_service.list_all(page_filter=page_filter, user_request='ash')

        assert hasattr(result, 'items')
        assert len(result.items) == 0
        assert hasattr(result, 'meta')
        meta = result.meta
        assert meta.total == 0


class TestPokemonServiceListAllCached:
    """Test scope for list_all_cached method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_service_list_all_cached_success(pokemon, pokemon_service):
        """Should return list of pokemon when query is successful"""
        pokemon_service.pokemon_cache_service.build_key_all = AsyncMock(
            return_value='pokemon:list'
        )
        pokemon_service.pokemon_cache_service.get_all = AsyncMock(return_value=[pokemon])

        result = await pokemon_service.list_all_cached(user_request='guy')
        assert isinstance(result, list)
        assert len(result) == 1

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_service_list_all_cached_not_cached(pokemon, pokemon_service):
        with patch(
            'app.core.cache.redis.redis_client', new_callable=AsyncMock
        ) as mock_redis_client:
            mock_redis_client.setex.return_value = None
            pokemon_service.pokemon_cache_service.build_key_all = AsyncMock(
                return_value='pokemon:list'
            )
            pokemon_service.pokemon_cache_service.get_all = AsyncMock(return_value=None)

            pokemon_service.list_all = AsyncMock(return_value=[pokemon])

            with patch(
                'app.core.cache.manager.CacheManager.set_cache', new_callable=AsyncMock
            ) as mock_set_cache:
                mock_set_cache.return_value = None
                result = await pokemon_service.list_all_cached(user_request='rubens')
                assert isinstance(result, list)
                assert len(result) == 1


class TestPokemonServiceInitializeDatabase:
    @staticmethod
    @pytest.mark.asyncio
    async def test_initialize_database_with_zero_total_success(
        pokemon_service,
    ):
        total_result = 2
        external_pokemon_list = [
            SimpleNamespace(
                name='Bulbasaur',
                order=1,
                url='https://pokeapi.co/api/v2/pokemon/1',
                external_image='https://raw.githubusercontent.com/PokeAPI/sprites/1.png',
            ),
            SimpleNamespace(
                name='Ivysaur',
                order=2,
                url='https://pokeapi.co/api/v2/pokemon/2',
                external_image='https://raw.githubusercontent.com/PokeAPI/sprites/2.png',
            ),
        ]

        created_pokemons = [
            SimpleNamespace(
                id=1,
                name='Bulbasaur',
                order=1,
                status=StatusEnum.INCOMPLETE,
            ),
            SimpleNamespace(
                id=2,
                name='Ivysaur',
                order=2,
                status=StatusEnum.INCOMPLETE,
            ),
        ]
        pokemon_service.repository.save = AsyncMock(side_effect=created_pokemons)

        pokemon_service.external_service.pokemon_external_list = AsyncMock(
            return_value=external_pokemon_list
        )

        result = await pokemon_service.initialize_database(total=0)

        assert len(result) == total_result
        assert result[0].name == 'Bulbasaur'
        assert result[1].name == 'Ivysaur'
        assert pokemon_service.repository.save.call_count == total_result
        pokemon_service.external_service.pokemon_external_list.assert_called_once_with(
            offset=0, limit=1302
        )

    @staticmethod
    @pytest.mark.asyncio
    async def test_initialize_database_with_existing_data_add_missing(pokemon_service):
        """Should add only missing pokemon when database has data"""

        external_pokemon_list = [
            SimpleNamespace(
                name='Bulbasaur',
                order=1,
                url='https://pokeapi.co/api/v2/pokemon/1',
                external_image='https://raw.githubusercontent.com/PokeAPI/sprites/1.png',
            ),
            SimpleNamespace(
                name='Ivysaur',
                order=2,
                url='https://pokeapi.co/api/v2/pokemon/2',
                external_image='https://raw.githubusercontent.com/PokeAPI/sprites/2.png',
            ),
        ]

        existing_pokemons = [
            SimpleNamespace(name='Bulbasaur'),
        ]

        created_pokemon = SimpleNamespace(
            id=2,
            name='Ivysaur',
            order=2,
            status=StatusEnum.INCOMPLETE,
        )

        pokemon_service.external_service.pokemon_external_list = AsyncMock(
            return_value=external_pokemon_list
        )
        pokemon_service.repository.list_all = AsyncMock(return_value=existing_pokemons)
        pokemon_service.repository.save = AsyncMock(return_value=created_pokemon)

        result = await pokemon_service.initialize_database(total=1)

        assert len(result) == 1
        assert result[0].name == 'Ivysaur'
        pokemon_service.repository.list_all.assert_called_once()
        pokemon_service.repository.save.assert_called_once()

    @staticmethod
    @pytest.mark.asyncio
    async def test_initialize_database_with_all_existing_pokemon(pokemon_service):
        """Should not create any pokemon when all exist in database"""

        external_pokemon_list = [
            SimpleNamespace(
                name='Bulbasaur',
                order=1,
                url='https://pokeapi.co/api/v2/pokemon/1',
                external_image='https://raw.githubusercontent.com/PokeAPI/sprites/1.png',
            ),
            SimpleNamespace(
                name='Ivysaur',
                order=2,
                url='https://pokeapi.co/api/v2/pokemon/2',
                external_image='https://raw.githubusercontent.com/PokeAPI/sprites/2.png',
            ),
        ]

        existing_pokemons = [
            SimpleNamespace(name='Bulbasaur'),
            SimpleNamespace(name='Ivysaur'),
        ]

        pokemon_service.external_service.pokemon_external_list = AsyncMock(
            return_value=external_pokemon_list
        )
        pokemon_service.repository.list_all = AsyncMock(return_value=existing_pokemons)
        pokemon_service.repository.save = AsyncMock()

        result = await pokemon_service.initialize_database(total=2)

        assert len(result) == 0
        pokemon_service.repository.list_all.assert_called_once()
        pokemon_service.repository.save.assert_not_called()

    @staticmethod
    @pytest.mark.asyncio
    async def test_initialize_database_external_service_error(pokemon_service):
        """Should return empty list when external pokemon_service fails"""

        pokemon_service.external_service.pokemon_external_list = AsyncMock(
            side_effect=Exception('External API error')
        )
        pokemon_service.repository.save = AsyncMock()

        result = await pokemon_service.initialize_database(total=0)

        assert len(result) == 0
        assert isinstance(result, list)
        pokemon_service.repository.save.assert_not_called()

    @staticmethod
    @pytest.mark.asyncio
    async def test_initialize_database_repository_save_error_zero_total(pokemon_service):
        """Should handle repository error when creating pokemon with zero total"""

        external_pokemon_list = [
            SimpleNamespace(
                name='Bulbasaur',
                order=1,
                url='https://pokeapi.co/api/v2/pokemon/1',
                external_image='https://raw.githubusercontent.com/PokeAPI/sprites/1.png',
            ),
        ]

        pokemon_service.external_service.pokemon_external_list = AsyncMock(
            return_value=external_pokemon_list
        )
        pokemon_service.repository.save = AsyncMock(side_effect=Exception('Database error'))

        result = await pokemon_service.initialize_database(total=0)

        assert len(result) == 0
        assert isinstance(result, list)
        pokemon_service.repository.save.assert_called_once()

    @staticmethod
    @pytest.mark.asyncio
    async def test_initialize_database_repository_save_error_with_existing(pokemon_service):
        """Should handle repository error when creating missing pokemon"""

        external_pokemon_list = [
            SimpleNamespace(
                name='Bulbasaur',
                order=1,
                url='https://pokeapi.co/api/v2/pokemon/1',
                external_image='https://raw.githubusercontent.com/PokeAPI/sprites/1.png',
            ),
            SimpleNamespace(
                name='Ivysaur',
                order=2,
                url='https://pokeapi.co/api/v2/pokemon/2',
                external_image='https://raw.githubusercontent.com/PokeAPI/sprites/2.png',
            ),
        ]

        existing_pokemons = [
            SimpleNamespace(name='Bulbasaur'),
        ]

        pokemon_service.external_service.pokemon_external_list = AsyncMock(
            return_value=external_pokemon_list
        )
        pokemon_service.repository.list_all = AsyncMock(return_value=existing_pokemons)
        pokemon_service.repository.save = AsyncMock(side_effect=Exception('Database error'))

        result = await pokemon_service.initialize_database(total=1)

        assert len(result) == 0
        assert isinstance(result, list)
        pokemon_service.repository.save.assert_called_once()

    @staticmethod
    @pytest.mark.asyncio
    async def test_initialize_database_empty_external_list(pokemon_service):
        """Should return empty list when external pokemon_service returns no pokemon"""

        pokemon_service.external_service.pokemon_external_list = AsyncMock(return_value=[])
        pokemon_service.repository.save = AsyncMock()

        result = await pokemon_service.initialize_database(total=0)

        assert len(result) == 0
        assert isinstance(result, list)
        pokemon_service.external_service.pokemon_external_list.assert_called_once_with(
            offset=0, limit=1302
        )
        pokemon_service.repository.save.assert_not_called()

    @staticmethod
    @pytest.mark.asyncio
    async def test_initialize_database_preserves_pokemon_data(pokemon_service):
        """Should preserve pokemon attributes in created data"""

        external_pokemon_list = [
            SimpleNamespace(
                name='Pikachu',
                order=25,
                url='https://pokeapi.co/api/v2/pokemon/25',
                external_image='https://raw.githubusercontent.com/PokeAPI/sprites/25.png',
            ),
        ]
        created_pokemon_order = 25
        created_pokemon = SimpleNamespace(
            id=1,
            name='Pikachu',
            order=created_pokemon_order,
            url='https://pokeapi.co/api/v2/pokemon/25',
            external_image='https://raw.githubusercontent.com/PokeAPI/sprites/25.png',
            status=StatusEnum.INCOMPLETE,
        )

        pokemon_service.external_service.pokemon_external_list = AsyncMock(
            return_value=external_pokemon_list
        )
        pokemon_service.repository.save = AsyncMock(return_value=created_pokemon)

        result = await pokemon_service.initialize_database(total=0)

        assert len(result) == 1
        assert result[0].order == created_pokemon_order
        assert result[0].name == 'Pikachu'
        assert result[0].url == 'https://pokeapi.co/api/v2/pokemon/25'
        assert (
            result[0].external_image
            == 'https://raw.githubusercontent.com/PokeAPI/sprites/25.png'
        )

    @staticmethod
    @pytest.mark.asyncio
    async def test_initialize_database_calls_correct_save_entity(pokemon_service):
        """Should call save with correct Pokemon entity attributes"""

        external_pokemon = SimpleNamespace(
            name='Dragonite',
            order=MOCK_ENTITY_ORDER,
            url='https://pokeapi.co/api/v2/pokemon/149',
            external_image='https://raw.githubusercontent.com/PokeAPI/sprites/149.png',
        )

        created_pokemon = SimpleNamespace(
            id=1,
            name='Dragonite',
            order=MOCK_ENTITY_ORDER,
        )

        pokemon_service.external_service.pokemon_external_list = AsyncMock(
            return_value=[external_pokemon]
        )
        pokemon_service.repository.save = AsyncMock(return_value=created_pokemon)

        await pokemon_service.initialize_database(total=0)

        call_args = pokemon_service.repository.save.call_args
        pokemon_entity = call_args.kwargs['entity']

        assert pokemon_entity.name == 'Dragonite'
        assert pokemon_entity.order == MOCK_ENTITY_ORDER
        assert pokemon_entity.url == 'https://pokeapi.co/api/v2/pokemon/149'
        assert pokemon_entity.status == StatusEnum.INCOMPLETE
        assert (
            pokemon_entity.external_image
            == 'https://raw.githubusercontent.com/PokeAPI/sprites/149.png'
        )


class TestPokemonServiceFetchOne:
    """Test scope for fetch_one method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_fetch_one_success_with_complete_pokemon(pokemon_service):
        """Should return complete pokemon when found"""
        pokemon = Pokemon(
            name='pikachu',
            order=25,
            url='https://pokeapi.co/api/v2/pokemon/25/',
            status=StatusEnum.COMPLETE,
            external_image='https://example.com/25.png',
        )

        pokemon_service.repository.find_by = AsyncMock(return_value=pokemon)

        result = await pokemon_service.fetch_one(name='pikachu', user_request='ash')

        assert result is not None
        assert result.name == 'pikachu'
        assert result.status == StatusEnum.COMPLETE
        pokemon_service.repository.find_by.assert_called_once_with(name='pikachu')

    @staticmethod
    @pytest.mark.asyncio
    async def test_fetch_one_not_found_raises_exception(pokemon_service):
        """Should raise HTTPException when pokemon not found"""

        pokemon_service.repository.find_by = AsyncMock(return_value=None)

        with pytest.raises(HTTPException) as exc_info:
            await pokemon_service.fetch_one(name='nonexistent', user_request='john')

        assert exc_info.value.status_code == HTTPStatus.NOT_FOUND
        assert exc_info.value.detail == 'Pokemon not found'

    @staticmethod
    @pytest.mark.asyncio
    async def test_fetch_one_incomplete_pokemon_completes_data(pokemon_service):
        """Should complete pokemon data when status is incomplete"""
        incomplete_pokemon = Pokemon(
            name='bulbasaur',
            order=1,
            url='https://pokeapi.co/api/v2/pokemon/1/',
            status=StatusEnum.INCOMPLETE,
            external_image='https://example.com/1.png',
        )

        completed_pokemon = Pokemon(
            name='bulbasaur',
            order=1,
            url='https://pokeapi.co/api/v2/pokemon/1/',
            status=StatusEnum.COMPLETE,
            external_image='https://example.com/1.png',
            hp=45,
        )

        pokemon_service.repository.find_by = AsyncMock(return_value=incomplete_pokemon)
        pokemon_service.complete_pokemon_data = AsyncMock(return_value=completed_pokemon)

        result = await pokemon_service.fetch_one(name='bulbasaur', user_request='judy')

        assert result is not None
        assert result.status == StatusEnum.COMPLETE
        pokemon_service.complete_pokemon_data.assert_called_once()


class TestPokemonServiceFetchOneCached:
    """Test scope for fetch_one_cached method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_service_fetch_one_cached_success(pokemon, pokemon_service):
        """Should return complete pokemon when found"""
        pokemon_service.pokemon_cache_service.build_key_one = AsyncMock(
            return_value=f'pokemon:{pokemon.name}'
        )
        pokemon_service.pokemon_cache_service.get_one = AsyncMock(return_value=pokemon)
        result = await pokemon_service.fetch_one_cached(name=pokemon.name, user_request='guy')
        assert result is not None
        assert result.name == pokemon.name
        assert result.status == StatusEnum.COMPLETE

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_service_fetch_one_not_cached(pokemon, pokemon_service):
        """Should return complete pokemon when found"""
        with patch(
            'app.core.cache.redis.redis_client', new_callable=AsyncMock
        ) as mock_redis_client:
            mock_redis_client.setex.return_value = None
            pokemon_service.pokemon_cache_service.build_key_one = AsyncMock(
                return_value=f'pokemon:{pokemon.name}'
            )
            pokemon_service.pokemon_cache_service.get_one = AsyncMock(return_value=None)

            pokemon_service.fetch_one = AsyncMock(return_value=pokemon)

            with patch(
                'app.core.cache.manager.CacheManager.set_cache', new_callable=AsyncMock
            ) as mock_set_cache:
                mock_set_cache.return_value = None
                result = await pokemon_service.fetch_one_cached(
                    name=pokemon.name, user_request='rubens'
                )
                assert result is not None
                assert result.name == pokemon.name
                assert result.status == StatusEnum.COMPLETE


class TestPokemonServiceValidateEntity:
    """Test scope for validate_entity method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_validate_entity_returns_complete_pokemon(pokemon_service):
        """Should return pokemon when already complete"""
        pokemon = Pokemon(
            name='charizard',
            order=6,
            url='https://pokeapi.co/api/v2/pokemon/6/',
            status=StatusEnum.COMPLETE,
            external_image='https://example.com/6.png',
        )

        pokemon_service.repository.find_by = AsyncMock(return_value=pokemon)

        result = await pokemon_service.validate_entity(pokemon_name='charizard')

        assert result.name == 'charizard'
        assert result.status == StatusEnum.COMPLETE
        pokemon_service.repository.find_by.assert_called_once_with(name='charizard')

    @staticmethod
    @pytest.mark.asyncio
    async def test_validate_entity_not_found_raises_exception(pokemon_service):
        """Should raise HTTPException when pokemon not found"""

        pokemon_service.repository.find_by = AsyncMock(return_value=None)

        with pytest.raises(HTTPException) as exc_info:
            await pokemon_service.validate_entity(pokemon_name='missing')

        assert exc_info.value.status_code == HTTPStatus.NOT_FOUND
        assert exc_info.value.detail == 'Pokemon not found'

    @staticmethod
    @pytest.mark.asyncio
    async def test_validate_entity_completes_incomplete_pokemon(pokemon_service):
        """Should complete data when pokemon is incomplete"""
        incomplete_pokemon = Pokemon(
            name='squirtle',
            order=7,
            url='https://pokeapi.co/api/v2/pokemon/7/',
            status=StatusEnum.INCOMPLETE,
            external_image='https://example.com/7.png',
        )

        pokemon_service.repository.find_by = AsyncMock(return_value=incomplete_pokemon)
        pokemon_service.complete_pokemon_data = AsyncMock(return_value=incomplete_pokemon)

        result = await pokemon_service.validate_entity(pokemon_name='squirtle')

        assert result is not None
        pokemon_service.complete_pokemon_data.assert_called_once_with(
            pokemon=incomplete_pokemon,
            with_evolutions=True,
        )

    @staticmethod
    @pytest.mark.asyncio
    async def test_validate_entity_with_evolutions_false(pokemon_service):
        """Should pass with_evolutions=False to complete_pokemon_data"""
        incomplete_pokemon = Pokemon(
            name='eevee',
            order=133,
            url='https://pokeapi.co/api/v2/pokemon/133/',
            status=StatusEnum.INCOMPLETE,
            external_image='https://example.com/133.png',
        )

        pokemon_service.repository.find_by = AsyncMock(return_value=incomplete_pokemon)
        pokemon_service.complete_pokemon_data = AsyncMock(return_value=incomplete_pokemon)

        result = await pokemon_service.validate_entity(
            pokemon_name='eevee',
            with_evolutions=False,
        )

        assert result is not None
        pokemon_service.complete_pokemon_data.assert_called_once_with(
            pokemon=incomplete_pokemon,
            with_evolutions=False,
        )


class TestPokemonServiceCompletePokemonData:
    """Test scope for complete_pokemon_data method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_complete_pokemon_data_success_with_evolutions(pokemon_service):
        """Should complete pokemon data and attach evolutions when enabled"""
        now = datetime.now()
        pokemon = Pokemon(
            name='bulbasaur',
            order=1,
            url='https://pokeapi.co/api/v2/pokemon/1/',
            status=StatusEnum.INCOMPLETE,
            external_image='https://example.com/1.png',
        )
        pokemon.id = 'pokemon-id-1'
        pokemon.created_at = now
        pokemon.updated_at = now
        growth_rate = MOCK_POKEMON_GROWTH_RATE
        growth_rate.id = 'growth-rate-id'
        external_pokemon = SimpleNamespace(
            name='bulbasaur',
            order=1,
            url='https://pokeapi.co/api/v2/pokemon/1/',
            external_image='https://example.com/1.png',
            evolution_chain_url='https://pokeapi.co/api/v2/evolution-chain/1/',
        )
        external_data = SimpleNamespace(
            pokemon=external_pokemon,
            moves=[{'move': {'url': 'https://pokeapi.co/api/v2/move/1/', 'name': 'tackle'}}],
            types=[
                {
                    'slot': 1,
                    'type': {'url': 'https://pokeapi.co/api/v2/type/12/', 'name': 'grass'},
                }
            ],
            abilities=[
                {
                    'slot': 1,
                    'is_hidden': False,
                    'ability': {
                        'url': 'https://pokeapi.co/api/v2/ability/65/',
                        'name': 'overgrow',
                    },
                }
            ],
            growth_rate={
                'url': 'https://pokeapi.co/api/v2/growth-rate/4/',
                'name': 'medium-slow',
            },
        )
        relationships = SimpleNamespace(
            moves=MOCK_POKEMON_MOVE_LIST,
            types=MOCK_POKEMON_TYPES_LIST,
            abilities=MOCK_POKEMON_ABILITIES_LIST,
            growth_rate=growth_rate,
            status=StatusEnum.COMPLETE,
        )
        evolutions = [
            Pokemon(
                name='ivysaur',
                order=2,
                url='https://pokeapi.co/api/v2/pokemon/2/',
                status=StatusEnum.COMPLETE,
                external_image='https://example.com/2.png',
            )
        ]
        evolutions[0].id = 'pokemon-id-2'
        evolutions[0].created_at = now
        evolutions[0].updated_at = now
        updated_pokemon = Pokemon(
            name='bulbasaur',
            order=1,
            url='https://pokeapi.co/api/v2/pokemon/1/',
            status=StatusEnum.COMPLETE,
            external_image='https://example.com/1.png',
        )
        updated_pokemon.id = 'pokemon-id-1'
        updated_pokemon.created_at = now
        updated_pokemon.updated_at = now

        pokemon_service.external_service.fetch_by_name = AsyncMock(return_value=external_data)
        pokemon_service.generate_relationships = AsyncMock(return_value=relationships)
        pokemon_service.add_evolutions = AsyncMock(return_value=evolutions)
        pokemon_service.business.merge_if_changed = MagicMock(return_value=updated_pokemon)
        pokemon_service.repository.update = AsyncMock()
        pokemon_service.repository.find_by = AsyncMock(return_value=updated_pokemon)

        result = await pokemon_service.complete_pokemon_data(
            pokemon=pokemon, with_evolutions=True
        )

        assert result.status == StatusEnum.COMPLETE
        assert result.name == 'bulbasaur'
        pokemon_service.external_service.fetch_by_name.assert_called_once()
        pokemon_service.generate_relationships.assert_called_once()
        pokemon_service.add_evolutions.assert_called_once_with(
            'https://pokeapi.co/api/v2/evolution-chain/1/'
        )
        pokemon_service.repository.update.assert_called_once()
        pokemon_service.repository.find_by.assert_called_once_with(name='bulbasaur')

    @staticmethod
    @pytest.mark.asyncio
    async def test_complete_pokemon_data_success_without_evolutions(pokemon_service):
        """Should complete pokemon data without evolutions when disabled"""
        now = datetime.now()
        pokemon = Pokemon(
            name='pikachu',
            order=25,
            url='https://pokeapi.co/api/v2/pokemon/25/',
            status=StatusEnum.INCOMPLETE,
            external_image='https://example.com/25.png',
        )
        pokemon.id = 'pokemon-id-25'
        pokemon.created_at = now
        pokemon.updated_at = now
        external_pokemon = SimpleNamespace(
            name='pikachu',
            order=25,
            url='https://pokeapi.co/api/v2/pokemon/25/',
            external_image='https://example.com/25.png',
            evolution_chain_url='https://pokeapi.co/api/v2/evolution-chain/10/',
        )
        external_data = SimpleNamespace(
            pokemon=external_pokemon,
            moves=[{'move': {'url': 'https://pokeapi.co/api/v2/move/1/', 'name': 'tackle'}}],
            types=[
                {
                    'slot': 1,
                    'type': {'url': 'https://pokeapi.co/api/v2/type/13/', 'name': 'electric'},
                }
            ],
            abilities=[
                {
                    'slot': 1,
                    'is_hidden': False,
                    'ability': {
                        'url': 'https://pokeapi.co/api/v2/ability/9/',
                        'name': 'static',
                    },
                }
            ],
            growth_rate=None,
        )
        relationships = SimpleNamespace(
            moves=MOCK_POKEMON_MOVE_LIST,
            types=MOCK_POKEMON_TYPES_LIST,
            abilities=MOCK_POKEMON_ABILITIES_LIST,
            growth_rate=None,
            status=StatusEnum.INCOMPLETE,
        )
        updated_pokemon = Pokemon(
            name='pikachu',
            order=25,
            url='https://pokeapi.co/api/v2/pokemon/25/',
            status=StatusEnum.INCOMPLETE,
            external_image='https://example.com/25.png',
        )
        updated_pokemon.id = 'pokemon-id-25'
        updated_pokemon.created_at = now
        updated_pokemon.updated_at = now

        pokemon_service.external_service.fetch_by_name = AsyncMock(return_value=external_data)
        pokemon_service.generate_relationships = AsyncMock(return_value=relationships)
        pokemon_service.add_evolutions = AsyncMock()
        pokemon_service.business.merge_if_changed = MagicMock(return_value=updated_pokemon)
        pokemon_service.repository.update = AsyncMock()
        pokemon_service.repository.find_by = AsyncMock(return_value=updated_pokemon)

        result = await pokemon_service.complete_pokemon_data(
            pokemon=pokemon, with_evolutions=False
        )

        assert result.name == 'pikachu'
        pokemon_service.add_evolutions.assert_not_called()
        pokemon_service.repository.update.assert_called_once()

    @staticmethod
    @pytest.mark.asyncio
    async def test_complete_pokemon_data_raises_http_exception(pokemon_service):
        """Should re-raise HTTPException when external pokemon_service fails"""
        now = datetime.now()
        pokemon = Pokemon(
            name='eevee',
            order=133,
            url='https://pokeapi.co/api/v2/pokemon/133/',
            status=StatusEnum.INCOMPLETE,
            external_image='https://example.com/133.png',
        )
        pokemon.id = 'pokemon-id-133'
        pokemon.created_at = now
        pokemon.updated_at = now

        pokemon_service.external_service.fetch_by_name = AsyncMock(
            side_effect=HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='error')
        )

        with pytest.raises(HTTPException) as exc_info:
            await pokemon_service.complete_pokemon_data(pokemon=pokemon, with_evolutions=True)

        assert exc_info.value.status_code == HTTPStatus.BAD_REQUEST

    @staticmethod
    @pytest.mark.asyncio
    async def test_complete_pokemon_data_unexpected_error(pokemon_service):
        """Should raise HTTPException when unexpected error occurs"""
        now = datetime.now()
        pokemon = Pokemon(
            name='mew',
            order=151,
            url='https://pokeapi.co/api/v2/pokemon/151/',
            status=StatusEnum.INCOMPLETE,
            external_image='https://example.com/151.png',
        )
        pokemon.id = 'pokemon-id-151'
        pokemon.created_at = now
        pokemon.updated_at = now

        pokemon_service.external_service.fetch_by_name = AsyncMock(
            side_effect=Exception('boom')
        )

        with pytest.raises(HTTPException) as exc_info:
            await pokemon_service.complete_pokemon_data(pokemon=pokemon, with_evolutions=True)

        assert exc_info.value.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert exc_info.value.detail == 'Internal server error'


class TestPokemonServiceAddEvolutions:
    """Test scope for add_evolutions method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_add_evolutions_returns_empty_when_url_is_none(pokemon_service):
        """Should return empty list when evolution_chain_url is None"""

        result = await pokemon_service.add_evolutions(evolution_chain_url=None)

        assert result == []
        assert isinstance(result, list)

    @staticmethod
    @pytest.mark.asyncio
    async def test_add_evolutions_returns_empty_when_chain_is_none(pokemon_service):
        """Should return empty list when external pokemon_service returns None"""

        pokemon_service.external_service.pokemon_external_evolution_by_url = AsyncMock(
            return_value=None
        )

        result = await pokemon_service.add_evolutions(
            evolution_chain_url='https://pokeapi.co/api/v2/evolution-chain/1/'
        )

        assert result == []

    @staticmethod
    @pytest.mark.asyncio
    async def test_add_evolutions_success_with_single_evolution(pokemon_service):
        """Should return evolution list when chain exists"""
        evolution_chain = SimpleNamespace(
            chain=SimpleNamespace(
                species=SimpleNamespace(name='bulbasaur'),
                evolves_to=[],
            )
        )

        pokemon = Pokemon(
            name='bulbasaur',
            order=1,
            url='https://pokeapi.co/api/v2/pokemon/1/',
            status=StatusEnum.COMPLETE,
            external_image='https://example.com/1.png',
        )

        pokemon_service.external_service.pokemon_external_evolution_by_url = AsyncMock(
            return_value=evolution_chain
        )
        pokemon_service.business.ensure_evolution = lambda x: ['bulbasaur']
        pokemon_service.validate_entity = AsyncMock(return_value=pokemon)

        result = await pokemon_service.add_evolutions(
            evolution_chain_url='https://pokeapi.co/api/v2/evolution-chain/1/'
        )

        assert len(result) == 1
        assert result[0].name == 'bulbasaur'

    @staticmethod
    @pytest.mark.asyncio
    async def test_add_evolutions_handles_exception(pokemon_service):
        """Should return empty list when exception occurs"""

        pokemon_service.external_service.pokemon_external_evolution_by_url = AsyncMock(
            side_effect=Exception('API error')
        )

        result = await pokemon_service.add_evolutions(
            evolution_chain_url='https://pokeapi.co/api/v2/evolution-chain/1/'
        )

        assert result == []


class TestPokemonServiceGenerateRelationships:
    """Test scope for generate_relationships method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_generate_relationships_success_with_all_data(pokemon_service):
        """Should return complete relationships when all data is valid"""

        relationships = MOCK_RELATIONSHIPS

        pokemon_service.pokemon_move_service.verify_pokemon_move = AsyncMock(
            return_value=MOCK_POKEMON_MOVE_LIST
        )
        pokemon_service.pokemon_type_service.verify_pokemon_type = AsyncMock(
            return_value=MOCK_POKEMON_TYPES_LIST
        )
        pokemon_service.pokemon_ability_service.verify_pokemon_abilities = AsyncMock(
            return_value=MOCK_POKEMON_ABILITIES_LIST
        )
        pokemon_service.pokemon_growth_rate_service.verify_pokemon_growth_rate = AsyncMock(
            return_value=MOCK_POKEMON_GROWTH_RATE
        )

        result = await pokemon_service.generate_relationships(relationships=relationships)

        assert result.status == StatusEnum.COMPLETE
        assert len(result.moves) == 1
        assert len(result.types) == 1
        assert len(result.abilities) == 1
        assert result.growth_rate is not None

    @staticmethod
    @pytest.mark.asyncio
    async def test_generate_relationships_incomplete_when_moves_empty(pokemon_service):
        """Should return incomplete status when moves is empty"""

        pokemon_service.pokemon_move_service.verify_pokemon_move = AsyncMock(return_value=[])
        pokemon_service.pokemon_type_service.verify_pokemon_type = AsyncMock(
            return_value=MOCK_POKEMON_TYPES_LIST
        )
        pokemon_service.pokemon_ability_service.verify_pokemon_abilities = AsyncMock(
            return_value=MOCK_POKEMON_ABILITIES_LIST
        )
        pokemon_service.pokemon_growth_rate_service.verify_pokemon_growth_rate = AsyncMock(
            return_value=MOCK_POKEMON_GROWTH_RATE
        )

        result = await pokemon_service.generate_relationships(relationships=MOCK_RELATIONSHIPS)

        assert result.status == StatusEnum.INCOMPLETE

    @staticmethod
    @pytest.mark.asyncio
    async def test_generate_relationships_incomplete_when_types_empty(pokemon_service):
        """Should return incomplete status when types is empty"""

        pokemon_service.pokemon_move_service.verify_pokemon_move = AsyncMock(
            return_value=MOCK_POKEMON_MOVE_LIST
        )
        pokemon_service.pokemon_type_service.verify_pokemon_type = AsyncMock(return_value=[])
        pokemon_service.pokemon_ability_service.verify_pokemon_abilities = AsyncMock(
            return_value=MOCK_POKEMON_ABILITIES_LIST
        )
        pokemon_service.pokemon_growth_rate_service.verify_pokemon_growth_rate = AsyncMock(
            return_value=MOCK_POKEMON_GROWTH_RATE
        )

        result = await pokemon_service.generate_relationships(relationships=MOCK_RELATIONSHIPS)

        assert result.status == StatusEnum.INCOMPLETE

    @staticmethod
    @pytest.mark.asyncio
    async def test_generate_relationships_incomplete_when_abilities_empty(pokemon_service):
        """Should return incomplete status when abilities is empty"""

        pokemon_service.pokemon_move_service.verify_pokemon_move = AsyncMock(
            return_value=MOCK_POKEMON_MOVE_LIST
        )
        pokemon_service.pokemon_type_service.verify_pokemon_type = AsyncMock(
            return_value=MOCK_POKEMON_TYPES_LIST
        )
        pokemon_service.pokemon_ability_service.verify_pokemon_abilities = AsyncMock(
            return_value=[]
        )
        pokemon_service.pokemon_growth_rate_service.verify_pokemon_growth_rate = AsyncMock(
            return_value=MOCK_POKEMON_GROWTH_RATE
        )

        result = await pokemon_service.generate_relationships(relationships=MOCK_RELATIONSHIPS)

        assert result.status == StatusEnum.INCOMPLETE

    @staticmethod
    @pytest.mark.asyncio
    async def test_generate_relationships_incomplete_when_growth_rate_none(pokemon_service):
        """Should return complete status when growth_rate is None but other data is valid"""

        pokemon_service.pokemon_move_service.verify_pokemon_move = AsyncMock(
            return_value=MOCK_POKEMON_MOVE_LIST
        )
        pokemon_service.pokemon_type_service.verify_pokemon_type = AsyncMock(
            return_value=MOCK_POKEMON_TYPES_LIST
        )
        pokemon_service.pokemon_ability_service.verify_pokemon_abilities = AsyncMock(
            return_value=MOCK_POKEMON_ABILITIES_LIST
        )
        pokemon_service.pokemon_growth_rate_service.verify_pokemon_growth_rate = AsyncMock(
            return_value=None
        )

        result = await pokemon_service.generate_relationships(relationships=MOCK_RELATIONSHIPS)

        assert result.status == StatusEnum.COMPLETE
        assert result.growth_rate is None


class TestPokemonServiceFirstPokemon:
    """Test scope for first_pokemon method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_first_pokemon_with_name_found(pokemon_service):
        """Should return pokemon when name is found"""
        bulbasaur = Pokemon(
            name='bulbasaur',
            order=1,
            url='https://pokeapi.co/api/v2/pokemon/1/',
            status=StatusEnum.COMPLETE,
            external_image='https://example.com/1.png',
        )
        bulbasaur.id = str(uuid4())

        pokemon_service.list_all = AsyncMock(return_value=[bulbasaur])
        pokemon_service.fetch_one = AsyncMock(return_value=bulbasaur)

        result = await pokemon_service.first_pokemon(name='bulbasaur')

        assert result is not None
        assert result.pokemon is not None
        assert result.pokemon.name == 'bulbasaur'
        pokemon_service.list_all.assert_called_once()
        pokemon_service.fetch_one.assert_called_once_with(name='bulbasaur')

    @staticmethod
    @pytest.mark.asyncio
    async def test_first_pokemon_with_name_not_found(pokemon_service):
        """Should return random complete pokemon when name is not found"""
        bulbasaur = Pokemon(
            name='bulbasaur',
            order=1,
            url='https://pokeapi.co/api/v2/pokemon/1/',
            status=StatusEnum.COMPLETE,
            external_image='https://example.com/1.png',
        )
        pikachu = Pokemon(
            name='pikachu',
            order=25,
            url='https://pokeapi.co/api/v2/pokemon/25/',
            status=StatusEnum.INCOMPLETE,
            external_image='https://example.com/25.png',
        )
        bulbasaur.id = str(uuid4())
        pikachu.id = str(uuid4())
        pokemons = [bulbasaur, pikachu]

        pokemon_service.list_all = AsyncMock(return_value=pokemons)
        pokemon_service.fetch_one = AsyncMock(return_value=bulbasaur)
        pokemon_service.business.find_first_pokemon = MagicMock(return_value=bulbasaur)

        result = await pokemon_service.first_pokemon(name='nonexistent')

        assert result is not None
        assert result.pokemon is not None
        assert result.pokemon.name == 'bulbasaur'
        pokemon_service.list_all.assert_called_once()
        pokemon_service.fetch_one.assert_called_once_with(name='bulbasaur')

    @staticmethod
    @pytest.mark.asyncio
    async def test_first_pokemon_without_name(pokemon_service):
        """Should return random complete pokemon when name is None"""
        bulbasaur = Pokemon(
            name='bulbasaur',
            order=1,
            url='https://pokeapi.co/api/v2/pokemon/1/',
            status=StatusEnum.COMPLETE,
            external_image='https://example.com/1.png',
        )
        pikachu = Pokemon(
            name='pikachu',
            order=25,
            url='https://pokeapi.co/api/v2/pokemon/25/',
            status=StatusEnum.INCOMPLETE,
            external_image='https://example.com/25.png',
        )
        bulbasaur.id = str(uuid4())
        pikachu.id = str(uuid4())
        pokemons = [bulbasaur, pikachu]

        pokemon_service.list_all = AsyncMock(return_value=pokemons)
        pokemon_service.fetch_one = AsyncMock(return_value=bulbasaur)
        pokemon_service.business.find_first_pokemon = MagicMock(return_value=bulbasaur)

        result = await pokemon_service.first_pokemon(name=None)

        assert result is not None
        assert result.pokemon is not None
        assert result.pokemon.name == 'bulbasaur'
        pokemon_service.list_all.assert_called_once()
        pokemon_service.fetch_one.assert_called_once_with(name='bulbasaur')

    @staticmethod
    @pytest.mark.asyncio
    async def test_first_pokemon_with_no_complete_pokemon(pokemon_service):
        """Should return FirstPokemonSchemaResult with pokemon=None when no complete exists"""
        pikachu = Pokemon(
            name='pikachu',
            order=25,
            url='https://pokeapi.co/api/v2/pokemon/25/',
            status=StatusEnum.INCOMPLETE,
            external_image='https://example.com/25.png',
        )
        charmander = Pokemon(
            name='charmander',
            order=4,
            url='https://pokeapi.co/api/v2/pokemon/4/',
            status=StatusEnum.INCOMPLETE,
            external_image='https://example.com/4.png',
        )
        pikachu.id = str(uuid4())
        charmander.id = str(uuid4())
        pokemons = [pikachu, charmander]

        pokemon_service.list_all = AsyncMock(return_value=pokemons)
        pokemon_service.business.find_first_pokemon = MagicMock(return_value=None)

        result = await pokemon_service.first_pokemon(name=None)

        assert result is not None
        assert result.pokemon is None
        assert result.pokemons == pokemons
        pokemon_service.list_all.assert_called_once()

    @staticmethod
    @pytest.mark.asyncio
    async def test_first_pokemon_with_empty_list(pokemon_service):
        """Should return FirstPokemonSchemaResult with pokemon=None when list is empty"""

        pokemon_service.list_all = AsyncMock(return_value=[])

        result = await pokemon_service.first_pokemon(name='bulbasaur')

        assert result is not None
        assert result.pokemon is None
        assert result.pokemons == []
        pokemon_service.list_all.assert_called_once()

    @staticmethod
    @pytest.mark.asyncio
    async def test_first_pokemon_with_multiple_complete(pokemon_service):
        """Should return the named pokemon if it exists in multiple complete pokemons"""
        bulbasaur = Pokemon(
            name='bulbasaur',
            order=1,
            url='https://pokeapi.co/api/v2/pokemon/1/',
            status=StatusEnum.COMPLETE,
            external_image='https://example.com/1.png',
        )
        ivysaur = Pokemon(
            name='ivysaur',
            order=2,
            url='https://pokeapi.co/api/v2/pokemon/2/',
            status=StatusEnum.COMPLETE,
            external_image='https://example.com/2.png',
        )
        venusaur = Pokemon(
            name='venusaur',
            order=3,
            url='https://pokeapi.co/api/v2/pokemon/3/',
            status=StatusEnum.COMPLETE,
            external_image='https://example.com/3.png',
        )
        bulbasaur.id = str(uuid4())
        ivysaur.id = str(uuid4())
        venusaur.id = str(uuid4())
        pokemons = [bulbasaur, ivysaur, venusaur]

        pokemon_service.list_all = AsyncMock(return_value=pokemons)
        pokemon_service.fetch_one = AsyncMock(return_value=ivysaur)

        result = await pokemon_service.first_pokemon(name='ivysaur')

        assert result is not None
        assert result.pokemon is not None
        assert result.pokemon.name == 'ivysaur'
        pokemon_service.fetch_one.assert_called_once_with(name='ivysaur')

    @staticmethod
    @pytest.mark.asyncio
    async def test_first_pokemon_raises_http_exception(pokemon_service):
        """Should raise HTTPException when fetch_all fails"""

        pokemon_service.list_all = AsyncMock(side_effect=Exception('Database error'))

        with pytest.raises(HTTPException) as exc_info:
            await pokemon_service.first_pokemon(name='bulbasaur')

        assert exc_info.value.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert exc_info.value.detail == 'Internal server error'

    @staticmethod
    @pytest.mark.asyncio
    async def test_first_pokemon_fetch_one_called_with_correct_name(pokemon_service):
        """Should call fetch_one with the pokemon name from find_first_pokemon"""
        bulbasaur = Pokemon(
            name='bulbasaur',
            order=1,
            url='https://pokeapi.co/api/v2/pokemon/1/',
            status=StatusEnum.COMPLETE,
            external_image='https://example.com/1.png',
        )
        pikachu = Pokemon(
            name='pikachu',
            order=25,
            url='https://pokeapi.co/api/v2/pokemon/25/',
            status=StatusEnum.INCOMPLETE,
            external_image='https://example.com/25.png',
        )
        bulbasaur.id = str(uuid4())
        pikachu.id = str(uuid4())
        pokemons = [pikachu, bulbasaur]
        returned_bulbasaur = Pokemon(
            name='bulbasaur',
            order=1,
            url='https://pokeapi.co/api/v2/pokemon/1/',
            status=StatusEnum.COMPLETE,
            external_image='https://example.com/1.png',
        )
        returned_bulbasaur.id = bulbasaur.id

        pokemon_service.list_all = AsyncMock(return_value=pokemons)
        pokemon_service.fetch_one = AsyncMock(return_value=returned_bulbasaur)

        result = await pokemon_service.first_pokemon(name=None)

        assert result is not None
        assert result.pokemon is not None
        pokemon_service.fetch_one.assert_called_once_with(name='bulbasaur')
