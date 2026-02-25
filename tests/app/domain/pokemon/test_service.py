from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.domain.pokemon.service import PokemonService
from app.shared.schemas import FilterPage
from app.shared.status_enum import StatusEnum
from tests.app.domain.pokemon.external.mocks.business_mock import (
    MOCK_ATTRIBUTES_ATTACK,
    MOCK_ATTRIBUTES_DEFENSE,
    MOCK_ATTRIBUTES_HP,
    MOCK_ATTRIBUTES_SPEED,
)
from tests.app.domain.pokemon.mock import MOCK_ENTITY_ORDER


class TestPokemonServiceInitializeDatabase:
    """Test scope for initialize_database method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_initialize_database_with_zero_total_success(session):
        """Should create all pokemon when database is empty"""
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
        total_result = 2
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

        service = PokemonService(session=session)
        service.external_service.pokemon_external_list = AsyncMock(
            return_value=external_pokemon_list
        )
        service.repository.create = AsyncMock(side_effect=created_pokemons)

        result = await service.initialize_database(total=0)

        assert len(result) == total_result
        assert result[0].name == 'Bulbasaur'
        assert result[1].name == 'Ivysaur'
        assert service.repository.create.call_count == total_result
        service.external_service.pokemon_external_list.assert_called_once_with(
            offset=0, limit=1302
        )

    @staticmethod
    @pytest.mark.asyncio
    async def test_initialize_database_with_existing_data_add_missing(session):
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

        service = PokemonService(session=session)
        service.external_service.pokemon_external_list = AsyncMock(
            return_value=external_pokemon_list
        )
        service.repository.list = AsyncMock(return_value=existing_pokemons)
        service.repository.create = AsyncMock(return_value=created_pokemon)

        result = await service.initialize_database(total=1)

        assert len(result) == 1
        assert result[0].name == 'Ivysaur'
        assert service.repository.create.call_count == 1
        service.repository.list.assert_called_once()

    @staticmethod
    @pytest.mark.asyncio
    async def test_initialize_database_with_all_existing_pokemon(session):
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

        service = PokemonService(session=session)
        service.external_service.pokemon_external_list = AsyncMock(
            return_value=external_pokemon_list
        )
        service.repository.list = AsyncMock(return_value=existing_pokemons)
        service.repository.create = AsyncMock()

        result = await service.initialize_database(total=2)

        assert len(result) == 0
        assert service.repository.create.call_count == 0
        service.repository.list.assert_called_once()

    @staticmethod
    @pytest.mark.asyncio
    async def test_initialize_database_external_service_error(session):
        """Should return empty list when external service fails"""

        service = PokemonService(session=session)
        service.external_service.pokemon_external_list = AsyncMock(
            side_effect=Exception('External API error')
        )
        service.repository.create = AsyncMock()

        result = await service.initialize_database(total=0)

        assert len(result) == 0
        assert isinstance(result, list)
        service.repository.create.assert_not_called()

    @staticmethod
    @pytest.mark.asyncio
    async def test_initialize_database_repository_create_error_zero_total(session):
        """Should handle repository error when creating pokemon with zero total"""

        external_pokemon_list = [
            SimpleNamespace(
                name='Bulbasaur',
                order=1,
                url='https://pokeapi.co/api/v2/pokemon/1',
                external_image='https://raw.githubusercontent.com/PokeAPI/sprites/1.png',
            ),
        ]

        service = PokemonService(session=session)
        service.external_service.pokemon_external_list = AsyncMock(
            return_value=external_pokemon_list
        )
        service.repository.create = AsyncMock(side_effect=Exception('Database error'))

        result = await service.initialize_database(total=0)

        assert len(result) == 0
        assert isinstance(result, list)
        service.repository.create.assert_called_once()

    @staticmethod
    @pytest.mark.asyncio
    async def test_initialize_database_repository_create_error_with_existing(session):
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

        service = PokemonService(session=session)
        service.external_service.pokemon_external_list = AsyncMock(
            return_value=external_pokemon_list
        )
        service.repository.list = AsyncMock(return_value=existing_pokemons)
        service.repository.create = AsyncMock(side_effect=Exception('Database error'))

        result = await service.initialize_database(total=1)

        assert len(result) == 0
        assert isinstance(result, list)
        service.repository.create.assert_called_once()

    @staticmethod
    @pytest.mark.asyncio
    async def test_initialize_database_empty_external_list(session):
        """Should return empty list when external service returns no pokemon"""

        service = PokemonService(session=session)
        service.external_service.pokemon_external_list = AsyncMock(return_value=[])
        service.repository.create = AsyncMock()

        result = await service.initialize_database(total=0)

        assert len(result) == 0
        assert isinstance(result, list)
        service.external_service.pokemon_external_list.assert_called_once_with(
            offset=0, limit=1302
        )
        service.repository.create.assert_not_called()

    @staticmethod
    @pytest.mark.asyncio
    async def test_initialize_database_preserves_pokemon_data(session):
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

        service = PokemonService(session=session)
        service.external_service.pokemon_external_list = AsyncMock(
            return_value=external_pokemon_list
        )
        service.repository.create = AsyncMock(return_value=created_pokemon)

        result = await service.initialize_database(total=0)

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
    async def test_initialize_database_calls_correct_create_schema(session):
        """Should call create with correct CreatePokemonSchema parameters"""

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

        service = PokemonService(session=session)
        service.external_service.pokemon_external_list = AsyncMock(
            return_value=[external_pokemon]
        )
        service.repository.create = AsyncMock(return_value=created_pokemon)

        await service.initialize_database(total=0)

        call_args = service.repository.create.call_args
        pokemon_schema = call_args.kwargs['pokemon_data']

        assert pokemon_schema.name == 'Dragonite'
        assert pokemon_schema.order == MOCK_ENTITY_ORDER
        assert pokemon_schema.url == 'https://pokeapi.co/api/v2/pokemon/149'
        assert (
            pokemon_schema.external_image
            == 'https://raw.githubusercontent.com/PokeAPI/sprites/149.png'
        )


class TestPokemonServiceFetchAll:
    """Test scope for fetch_all method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_fetch_all_success_with_complete_database(session):
        """Should return pokemon list when database has all pokemon"""
        pokemon_list = [
            SimpleNamespace(
                id=1,
                name='Bulbasaur',
                order=1,
                status=StatusEnum.COMPLETE,
            ),
            SimpleNamespace(
                id=2,
                name='Ivysaur',
                order=2,
                status=StatusEnum.COMPLETE,
            ),
        ]
        total_list = 2
        service = PokemonService(session=session)
        service.repository.total = AsyncMock(return_value=1302)
        service.repository.list = AsyncMock(return_value=pokemon_list)

        pokemon_filter = FilterPage(offset=0, limit=10)
        result = await service.fetch_all(pokemon_filter=pokemon_filter)

        assert len(result) == total_list
        assert result[0].name == 'Bulbasaur'
        assert result[1].name == 'Ivysaur'
        service.repository.total.assert_called_once()
        service.repository.list.assert_called_once_with(pokemon_filter=pokemon_filter)

    @staticmethod
    @pytest.mark.asyncio
    async def test_fetch_all_initializes_database_when_incomplete(session):
        """Should initialize database and return pokemon when total is less than limit"""
        pokemon_list = [
            SimpleNamespace(
                id=1,
                name='Charizard',
                order=6,
                status=StatusEnum.COMPLETE,
            ),
        ]

        service = PokemonService(session=session)
        service.repository.total = AsyncMock(return_value=100)
        service.initialize_database = AsyncMock(return_value=[])
        service.repository.list = AsyncMock(return_value=pokemon_list)

        pokemon_filter = FilterPage(offset=0, limit=10)
        result = await service.fetch_all(pokemon_filter=pokemon_filter)

        assert len(result) == 1
        assert result[0].name == 'Charizard'
        service.repository.total.assert_called_once()
        service.initialize_database.assert_called_once_with(total=100)
        service.repository.list.assert_called_once_with(pokemon_filter=pokemon_filter)

    @staticmethod
    @pytest.mark.asyncio
    async def test_fetch_all_with_offset_and_limit(session):
        """Should apply offset and limit filters correctly"""
        pokemon_list = [
            SimpleNamespace(
                id=11,
                name='Pidgeot',
                order=11,
                status=StatusEnum.COMPLETE,
            ),
        ]

        service = PokemonService(session=session)
        service.repository.total = AsyncMock(return_value=1302)
        service.repository.list = AsyncMock(return_value=pokemon_list)

        pokemon_filter = FilterPage(offset=10, limit=1)
        result = await service.fetch_all(pokemon_filter=pokemon_filter)

        assert len(result) == 1
        assert result[0].name == 'Pidgeot'
        service.repository.list.assert_called_once_with(pokemon_filter=pokemon_filter)

    @staticmethod
    @pytest.mark.asyncio
    async def test_fetch_all_returns_empty_list_on_error(session):
        """Should return empty list when repository raises exception"""
        service = PokemonService(session=session)
        service.repository.total = AsyncMock(side_effect=Exception('Database error'))

        pokemon_filter = FilterPage(offset=0, limit=10)
        result = await service.fetch_all(pokemon_filter=pokemon_filter)

        assert result == []
        assert isinstance(result, list)

    @staticmethod
    @pytest.mark.asyncio
    async def test_fetch_all_returns_empty_list_on_list_error(session):
        """Should return empty list when list query fails"""
        service = PokemonService(session=session)
        service.repository.total = AsyncMock(return_value=1302)
        service.repository.list = AsyncMock(side_effect=Exception('Query error'))

        pokemon_filter = FilterPage(offset=0, limit=10)
        result = await service.fetch_all(pokemon_filter=pokemon_filter)

        assert result == []
        assert isinstance(result, list)

    @staticmethod
    @pytest.mark.asyncio
    async def test_fetch_all_returns_empty_list_when_initialization_fails(session):
        """Should return empty list when initialize_database fails"""
        service = PokemonService(session=session)
        service.repository.total = AsyncMock(return_value=100)
        service.initialize_database = AsyncMock(side_effect=Exception('Initialization error'))

        pokemon_filter = FilterPage(offset=0, limit=10)
        result = await service.fetch_all(pokemon_filter=pokemon_filter)

        assert result == []
        assert isinstance(result, list)

    @staticmethod
    @pytest.mark.asyncio
    async def test_fetch_all_empty_result_when_no_pokemon(session):
        """Should return empty list when no pokemon exists"""
        service = PokemonService(session=session)
        service.repository.total = AsyncMock(return_value=1302)
        service.repository.list = AsyncMock(return_value=[])

        pokemon_filter = FilterPage(offset=0, limit=10)
        result = await service.fetch_all(pokemon_filter=pokemon_filter)

        assert result == []
        assert isinstance(result, list)

    @staticmethod
    @pytest.mark.asyncio
    async def test_fetch_all_with_large_offset(session):
        """Should handle large offset correctly"""
        pokemon_list = []

        service = PokemonService(session=session)
        service.repository.total = AsyncMock(return_value=1302)
        service.repository.list = AsyncMock(return_value=pokemon_list)

        pokemon_filter = FilterPage(offset=1300, limit=10)
        result = await service.fetch_all(pokemon_filter=pokemon_filter)

        assert result == []
        service.repository.list.assert_called_once_with(pokemon_filter=pokemon_filter)

    @staticmethod
    @pytest.mark.asyncio
    async def test_fetch_all_preserves_pokemon_attributes(session):
        """Should preserve all pokemon attributes in result"""
        total_list = 1
        pokemon_list = [
            SimpleNamespace(
                id='8742059c-fa5d-41c8-b95c-fb51bf60f5aa',
                name='Pikachu',
                order=MOCK_ENTITY_ORDER,
                status=StatusEnum.COMPLETE,
                hp=MOCK_ATTRIBUTES_HP,
                attack=MOCK_ATTRIBUTES_ATTACK,
                defense=MOCK_ATTRIBUTES_DEFENSE,
                speed=MOCK_ATTRIBUTES_SPEED,
            ),
        ]

        service = PokemonService(session=session)
        service.repository.total = AsyncMock(return_value=1302)
        service.repository.list = AsyncMock(return_value=pokemon_list)

        pokemon_filter = FilterPage(offset=0, limit=10)
        result = await service.fetch_all(pokemon_filter=pokemon_filter)

        assert len(result) == total_list
        assert result[0].name == 'Pikachu'
        assert result[0].order == MOCK_ENTITY_ORDER
        assert result[0].hp == MOCK_ATTRIBUTES_HP
        assert result[0].attack == MOCK_ATTRIBUTES_ATTACK
        assert result[0].defense == MOCK_ATTRIBUTES_DEFENSE
        assert result[0].speed == MOCK_ATTRIBUTES_SPEED

    @staticmethod
    @pytest.mark.asyncio
    async def test_fetch_all_does_not_initialize_when_total_equals_limit(session):
        """Should not call initialize_database when total equals POKEMON_TOTAL_LIMIT"""
        pokemon_list = [
            SimpleNamespace(
                id=1,
                name='Bulbasaur',
                order=1,
                status=StatusEnum.COMPLETE,
            ),
        ]

        service = PokemonService(session=session)
        service.repository.total = AsyncMock(return_value=1302)
        service.initialize_database = AsyncMock()
        service.repository.list = AsyncMock(return_value=pokemon_list)

        pokemon_filter = FilterPage(offset=0, limit=10)
        result = await service.fetch_all(pokemon_filter=pokemon_filter)

        assert len(result) == 1
        service.initialize_database.assert_not_called()
        service.repository.list.assert_called_once()

    @staticmethod
    @pytest.mark.asyncio
    async def test_fetch_all_initializes_when_total_less_than_limit(session):
        """Should call initialize_database when total is less than POKEMON_TOTAL_LIMIT"""
        pokemon_list = []

        service = PokemonService(session=session)
        service.repository.total = AsyncMock(return_value=500)
        service.initialize_database = AsyncMock(return_value=[])
        service.repository.list = AsyncMock(return_value=pokemon_list)

        pokemon_filter = FilterPage(offset=0, limit=10)
        result = await service.fetch_all(pokemon_filter=pokemon_filter)

        assert result == []
        service.initialize_database.assert_called_once_with(total=500)

    @staticmethod
    @pytest.mark.asyncio
    async def test_fetch_all_with_different_filter_configs(session):
        """Should respect different FilterPage configurations"""
        pokemon_list = [SimpleNamespace(name='Venusaur')]
        total_call_count = 3
        service = PokemonService(session=session)
        service.repository.total = AsyncMock(return_value=1302)
        service.repository.list = AsyncMock(return_value=pokemon_list)

        filters = [
            FilterPage(offset=0, limit=20),
            FilterPage(offset=50, limit=100),
            FilterPage(offset=1200, limit=102),
        ]

        for pokemon_filter in filters:
            result = await service.fetch_all(pokemon_filter=pokemon_filter)
            assert len(result) == 1

        assert service.repository.list.call_count == total_call_count
