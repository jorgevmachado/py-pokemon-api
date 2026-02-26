from datetime import datetime
from http import HTTPStatus
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from app.domain.pokemon.external.schemas import PokemonExternalBase
from app.domain.pokemon.schema import (
    GeneratePokemonRelationshipSchema,
)
from app.domain.pokemon.service import PokemonService
from app.models import Pokemon, PokemonAbility, PokemonGrowthRate, PokemonMove, PokemonType
from app.shared.schemas import FilterPage
from app.shared.status_enum import StatusEnum
from tests.app.domain.pokemon.external.mocks.business_mock import (
    MOCK_ATTRIBUTES_ATTACK,
    MOCK_ATTRIBUTES_DEFENSE,
    MOCK_ATTRIBUTES_HP,
    MOCK_ATTRIBUTES_SPEED,
)
from tests.app.domain.pokemon.mock import MOCK_ENTITY_ORDER

MOCK_POKEMON_MOVE_LIST = [
    PokemonMove(
        name='tackle',
        order=1,
        pp=35,
        url='https://pokeapi.co/api/v2/move/1/',
        type='normal',
        power=40,
        target='selected-pokemon',
        effect='Inflicts regular damage with no additional effect.',
        priority=0,
        accuracy=100,
        short_effect='Inflicts regular damage.',
        damage_class='physical',
        effect_chance=0,
    )
]
MOCK_POKEMON_TYPES_LIST = [
    PokemonType(
        name='grass',
        order=1,
        url='https://pokeapi.co/api/v2/type/12/',
        text_color='#ffffff',
        background_color='#78c850',
    )
]

MOCK_POKEMON_ABILITIES_LIST = [
    PokemonAbility(
        name='overgrow',
        order=1,
        url='https://pokeapi.co/api/v2/ability/65/',
        slot=1,
        is_hidden=False,
    )
]

MOCK_POKEMON_GROWTH_RATE = PokemonGrowthRate(
    name='medium-slow',
    order=1,
    url='https://pokeapi.co/api/v2/growth-rate/4/',
    formula='x^3',
)

MOCK_RELATIONSHIPS = GeneratePokemonRelationshipSchema(
    moves=[],
    types=[],
    abilities=[],
    growth_rate=PokemonExternalBase(
        url='https://pokeapi.co/api/v2/growth-rate/medium-slow/', name='medium-slow'
    ),
)


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


class TestPokemonServiceFetchOne:
    """Test scope for fetch_one method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_fetch_one_success_with_complete_pokemon(session):
        """Should return complete pokemon when found"""
        pokemon = Pokemon(
            name='pikachu',
            order=25,
            url='https://pokeapi.co/api/v2/pokemon/25/',
            status=StatusEnum.COMPLETE,
            external_image='https://example.com/25.png',
        )

        service = PokemonService(session=session)
        service.repository.find_one = AsyncMock(return_value=pokemon)

        result = await service.fetch_one(name='pikachu')

        assert result is not None
        assert result.name == 'pikachu'
        assert result.status == StatusEnum.COMPLETE
        service.repository.find_one.assert_called_once_with(name='pikachu')

    @staticmethod
    @pytest.mark.asyncio
    async def test_fetch_one_not_found_raises_exception(session):
        """Should raise HTTPException when pokemon not found"""
        service = PokemonService(session=session)
        service.repository.find_one = AsyncMock(return_value=None)

        with pytest.raises(HTTPException) as exc_info:
            await service.fetch_one(name='nonexistent')

        assert exc_info.value.status_code == HTTPStatus.NOT_FOUND
        assert exc_info.value.detail == 'Pokemon not found'

    @staticmethod
    @pytest.mark.asyncio
    async def test_fetch_one_incomplete_pokemon_completes_data(session):
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

        service = PokemonService(session=session)
        service.repository.find_one = AsyncMock(return_value=incomplete_pokemon)
        service.complete_pokemon_data = AsyncMock(return_value=completed_pokemon)

        result = await service.fetch_one(name='bulbasaur')

        assert result is not None
        assert result.status == StatusEnum.COMPLETE
        service.complete_pokemon_data.assert_called_once()


class TestPokemonServiceValidateEntity:
    """Test scope for validate_entity method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_validate_entity_returns_complete_pokemon(session):
        """Should return pokemon when already complete"""
        pokemon = Pokemon(
            name='charizard',
            order=6,
            url='https://pokeapi.co/api/v2/pokemon/6/',
            status=StatusEnum.COMPLETE,
            external_image='https://example.com/6.png',
        )

        service = PokemonService(session=session)
        service.repository.find_one = AsyncMock(return_value=pokemon)

        result = await service.validate_entity(pokemon_name='charizard')

        assert result.name == 'charizard'
        assert result.status == StatusEnum.COMPLETE
        service.repository.find_one.assert_called_once_with(name='charizard')

    @staticmethod
    @pytest.mark.asyncio
    async def test_validate_entity_not_found_raises_exception(session):
        """Should raise HTTPException when pokemon not found"""
        service = PokemonService(session=session)
        service.repository.find_one = AsyncMock(return_value=None)

        with pytest.raises(HTTPException) as exc_info:
            await service.validate_entity(pokemon_name='missing')

        assert exc_info.value.status_code == HTTPStatus.NOT_FOUND
        assert exc_info.value.detail == 'Pokemon not found'

    @staticmethod
    @pytest.mark.asyncio
    async def test_validate_entity_completes_incomplete_pokemon(session):
        """Should complete data when pokemon is incomplete"""
        incomplete_pokemon = Pokemon(
            name='squirtle',
            order=7,
            url='https://pokeapi.co/api/v2/pokemon/7/',
            status=StatusEnum.INCOMPLETE,
            external_image='https://example.com/7.png',
        )

        service = PokemonService(session=session)
        service.repository.find_one = AsyncMock(return_value=incomplete_pokemon)
        service.complete_pokemon_data = AsyncMock(return_value=incomplete_pokemon)

        result = await service.validate_entity(pokemon_name='squirtle')

        assert result is not None
        service.complete_pokemon_data.assert_called_once_with(
            pokemon=incomplete_pokemon,
            with_evolutions=True,
        )

    @staticmethod
    @pytest.mark.asyncio
    async def test_validate_entity_with_evolutions_false(session):
        """Should pass with_evolutions=False to complete_pokemon_data"""
        incomplete_pokemon = Pokemon(
            name='eevee',
            order=133,
            url='https://pokeapi.co/api/v2/pokemon/133/',
            status=StatusEnum.INCOMPLETE,
            external_image='https://example.com/133.png',
        )

        service = PokemonService(session=session)
        service.repository.find_one = AsyncMock(return_value=incomplete_pokemon)
        service.complete_pokemon_data = AsyncMock(return_value=incomplete_pokemon)

        result = await service.validate_entity(
            pokemon_name='eevee',
            with_evolutions=False,
        )

        assert result is not None
        service.complete_pokemon_data.assert_called_once_with(
            pokemon=incomplete_pokemon,
            with_evolutions=False,
        )


class TestPokemonServiceAddEvolutions:
    """Test scope for add_evolutions method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_add_evolutions_returns_empty_when_url_is_none(session):
        """Should return empty list when evolution_chain_url is None"""
        service = PokemonService(session=session)

        result = await service.add_evolutions(evolution_chain_url=None)

        assert result == []
        assert isinstance(result, list)

    @staticmethod
    @pytest.mark.asyncio
    async def test_add_evolutions_returns_empty_when_chain_is_none(session):
        """Should return empty list when external service returns None"""
        service = PokemonService(session=session)
        service.external_service.pokemon_external_evolution_by_url = AsyncMock(
            return_value=None
        )

        result = await service.add_evolutions(
            evolution_chain_url='https://pokeapi.co/api/v2/evolution-chain/1/'
        )

        assert result == []

    @staticmethod
    @pytest.mark.asyncio
    async def test_add_evolutions_success_with_single_evolution(session):
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

        service = PokemonService(session=session)
        service.external_service.pokemon_external_evolution_by_url = AsyncMock(
            return_value=evolution_chain
        )
        service.business.ensure_evolution = lambda x: ['bulbasaur']
        service.validate_entity = AsyncMock(return_value=pokemon)

        result = await service.add_evolutions(
            evolution_chain_url='https://pokeapi.co/api/v2/evolution-chain/1/'
        )

        assert len(result) == 1
        assert result[0].name == 'bulbasaur'

    @staticmethod
    @pytest.mark.asyncio
    async def test_add_evolutions_handles_exception(session):
        """Should return empty list when exception occurs"""
        service = PokemonService(session=session)
        service.external_service.pokemon_external_evolution_by_url = AsyncMock(
            side_effect=Exception('API error')
        )

        result = await service.add_evolutions(
            evolution_chain_url='https://pokeapi.co/api/v2/evolution-chain/1/'
        )

        assert result == []


class TestPokemonServiceGenerateRelationships:
    """Test scope for generate_relationships method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_generate_relationships_success_with_all_data(session):
        """Should return complete relationships when all data is valid"""

        relationships = GeneratePokemonRelationshipSchema(
            moves=[],
            types=[],
            abilities=[],
            growth_rate=PokemonExternalBase(
                url='https://pokeapi.co/api/v2/growth-rate/medium-slow/', name='medium-slow'
            ),
        )

        service = PokemonService(session=session)
        service.pokemon_move_service.verify_pokemon_move = AsyncMock(
            return_value=MOCK_POKEMON_MOVE_LIST
        )
        service.pokemon_type_service.verify_pokemon_type = AsyncMock(
            return_value=MOCK_POKEMON_TYPES_LIST
        )
        service.pokemon_ability_service.verify_pokemon_abilities = AsyncMock(
            return_value=MOCK_POKEMON_ABILITIES_LIST
        )
        service.pokemon_growth_rate_service.verify_pokemon_growth_rate = AsyncMock(
            return_value=MOCK_POKEMON_GROWTH_RATE
        )

        result = await service.generate_relationships(relationships=relationships)

        assert result.status == StatusEnum.COMPLETE
        assert len(result.moves) == 1
        assert len(result.types) == 1
        assert len(result.abilities) == 1
        assert result.growth_rate is not None

    @staticmethod
    @pytest.mark.asyncio
    async def test_generate_relationships_incomplete_when_moves_empty(session):
        """Should return incomplete status when moves is empty"""

        service = PokemonService(session=session)
        service.pokemon_move_service.verify_pokemon_move = AsyncMock(return_value=[])
        service.pokemon_type_service.verify_pokemon_type = AsyncMock(
            return_value=MOCK_POKEMON_TYPES_LIST
        )
        service.pokemon_ability_service.verify_pokemon_abilities = AsyncMock(
            return_value=MOCK_POKEMON_ABILITIES_LIST
        )
        service.pokemon_growth_rate_service.verify_pokemon_growth_rate = AsyncMock(
            return_value=MOCK_POKEMON_GROWTH_RATE
        )

        result = await service.generate_relationships(relationships=MOCK_RELATIONSHIPS)

        assert result.status == StatusEnum.INCOMPLETE

    @staticmethod
    @pytest.mark.asyncio
    async def test_generate_relationships_incomplete_when_types_empty(session):
        """Should return incomplete status when types is empty"""

        service = PokemonService(session=session)
        service.pokemon_move_service.verify_pokemon_move = AsyncMock(
            return_value=MOCK_POKEMON_MOVE_LIST
        )
        service.pokemon_type_service.verify_pokemon_type = AsyncMock(return_value=[])
        service.pokemon_ability_service.verify_pokemon_abilities = AsyncMock(
            return_value=MOCK_POKEMON_ABILITIES_LIST
        )
        service.pokemon_growth_rate_service.verify_pokemon_growth_rate = AsyncMock(
            return_value=MOCK_POKEMON_GROWTH_RATE
        )

        result = await service.generate_relationships(relationships=MOCK_RELATIONSHIPS)

        assert result.status == StatusEnum.INCOMPLETE

    @staticmethod
    @pytest.mark.asyncio
    async def test_generate_relationships_incomplete_when_abilities_empty(session):
        """Should return incomplete status when abilities is empty"""
        service = PokemonService(session=session)
        service.pokemon_move_service.verify_pokemon_move = AsyncMock(
            return_value=MOCK_POKEMON_MOVE_LIST
        )
        service.pokemon_type_service.verify_pokemon_type = AsyncMock(
            return_value=MOCK_POKEMON_TYPES_LIST
        )
        service.pokemon_ability_service.verify_pokemon_abilities = AsyncMock(return_value=[])
        service.pokemon_growth_rate_service.verify_pokemon_growth_rate = AsyncMock(
            return_value=MOCK_POKEMON_GROWTH_RATE
        )

        result = await service.generate_relationships(relationships=MOCK_RELATIONSHIPS)

        assert result.status == StatusEnum.INCOMPLETE

    @staticmethod
    @pytest.mark.asyncio
    async def test_generate_relationships_incomplete_when_growth_rate_none(session):
        """Should return incomplete status when growth_rate is None"""
        service = PokemonService(session=session)
        service.pokemon_move_service.verify_pokemon_move = AsyncMock(
            return_value=MOCK_POKEMON_MOVE_LIST
        )
        service.pokemon_type_service.verify_pokemon_type = AsyncMock(
            return_value=MOCK_POKEMON_TYPES_LIST
        )
        service.pokemon_ability_service.verify_pokemon_abilities = AsyncMock(
            return_value=MOCK_POKEMON_ABILITIES_LIST
        )
        service.pokemon_growth_rate_service.verify_pokemon_growth_rate = AsyncMock(
            return_value=None
        )

        result = await service.generate_relationships(relationships=MOCK_RELATIONSHIPS)

        assert result.status == StatusEnum.INCOMPLETE
        assert result.growth_rate is None


class TestPokemonServiceCompletePokemonData:
    """Test scope for complete_pokemon_data method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_complete_pokemon_data_success_with_evolutions(session):
        """Should complete pokemon data and attach evolutions when enabled"""
        now = datetime.utcnow()
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
        growth_rate = PokemonGrowthRate(
            name='medium-slow',
            order=1,
            url='https://pokeapi.co/api/v2/growth-rate/4/',
            formula='x^3',
        )
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

        service = PokemonService(session=session)
        service.external_service.fetch_by_name = AsyncMock(return_value=external_data)
        service.generate_relationships = AsyncMock(return_value=relationships)
        service.add_evolutions = AsyncMock(return_value=evolutions)
        service.business.merge_if_changed = AsyncMock(return_value=updated_pokemon)
        service.repository.update = AsyncMock()
        service.repository.find_one = AsyncMock(return_value=updated_pokemon)

        result = await service.complete_pokemon_data(pokemon=pokemon, with_evolutions=True)

        assert result.status == StatusEnum.COMPLETE
        assert result.name == 'bulbasaur'
        service.external_service.fetch_by_name.assert_called_once()
        service.generate_relationships.assert_called_once()
        service.add_evolutions.assert_called_once_with(
            'https://pokeapi.co/api/v2/evolution-chain/1/'
        )
        service.repository.update.assert_called_once()
        service.repository.find_one.assert_called_once_with(name='bulbasaur')

    @staticmethod
    @pytest.mark.asyncio
    async def test_complete_pokemon_data_success_without_evolutions(session):
        """Should complete pokemon data without evolutions when disabled"""
        now = datetime.utcnow()
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

        service = PokemonService(session=session)
        service.external_service.fetch_by_name = AsyncMock(return_value=external_data)
        service.generate_relationships = AsyncMock(return_value=relationships)
        service.add_evolutions = AsyncMock()
        service.business.merge_if_changed = AsyncMock(return_value=updated_pokemon)
        service.repository.update = AsyncMock()
        service.repository.find_one = AsyncMock(return_value=updated_pokemon)

        result = await service.complete_pokemon_data(pokemon=pokemon, with_evolutions=False)

        assert result.name == 'pikachu'
        service.add_evolutions.assert_not_called()
        service.repository.update.assert_called_once()

    @staticmethod
    @pytest.mark.asyncio
    async def test_complete_pokemon_data_raises_http_exception(session):
        """Should re-raise HTTPException when external service fails"""
        now = datetime.utcnow()
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
        service = PokemonService(session=session)
        service.external_service.fetch_by_name = AsyncMock(
            side_effect=HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='error')
        )

        with pytest.raises(HTTPException) as exc_info:
            await service.complete_pokemon_data(pokemon=pokemon, with_evolutions=True)

        assert exc_info.value.status_code == HTTPStatus.BAD_REQUEST

    @staticmethod
    @pytest.mark.asyncio
    async def test_complete_pokemon_data_unexpected_error(session):
        """Should raise HTTPException when unexpected error occurs"""
        now = datetime.utcnow()
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
        service = PokemonService(session=session)
        service.external_service.fetch_by_name = AsyncMock(side_effect=Exception('boom'))

        with pytest.raises(HTTPException) as exc_info:
            await service.complete_pokemon_data(pokemon=pokemon, with_evolutions=True)

        assert exc_info.value.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert exc_info.value.detail == 'Error completing pokemon data'
