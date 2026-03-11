from datetime import datetime
from http import HTTPStatus
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.domain.ability.model import PokemonAbility
from app.domain.growth_rate.model import PokemonGrowthRate
from app.domain.move.model import PokemonMove
from app.domain.pokemon.external.schemas import PokemonExternalBase
from app.domain.pokemon.model import Pokemon
from app.domain.pokemon.schema import (
    GeneratePokemonRelationshipSchema,
)
from app.domain.type.model import PokemonType
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

LIST_LIMIT = 10
LIST_OFFSET = 0
TOTAL_COUNT = 3


class TestPokemonServiceInitializeDatabase:
    """Test scope for initialize_database method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_initialize_database_with_zero_total_success(pokemon_service):
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

        pokemon_service.external_service.pokemon_external_list = AsyncMock(
            return_value=external_pokemon_list
        )
        pokemon_service.repository.create = AsyncMock(side_effect=created_pokemons)

        result = await pokemon_service.initialize_database(total=0)

        assert len(result) == total_result
        assert result[0].name == 'Bulbasaur'
        assert result[1].name == 'Ivysaur'
        assert pokemon_service.repository.create.call_count == total_result
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
        pokemon_service.repository.create = AsyncMock(return_value=created_pokemon)

        result = await pokemon_service.initialize_database(total=1)

        assert len(result) == 1
        assert result[0].name == 'Ivysaur'
        pokemon_service.repository.list_all.assert_called_once()
        pokemon_service.repository.create.assert_called_once()

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
        pokemon_service.repository.create = AsyncMock()

        result = await pokemon_service.initialize_database(total=2)

        assert len(result) == 0
        pokemon_service.repository.list_all.assert_called_once()
        pokemon_service.repository.create.assert_not_called()

    @staticmethod
    @pytest.mark.asyncio
    async def test_initialize_database_external_service_error(pokemon_service):
        """Should return empty list when external pokemon_service fails"""

        pokemon_service.external_service.pokemon_external_list = AsyncMock(
            side_effect=Exception('External API error')
        )
        pokemon_service.repository.create = AsyncMock()

        result = await pokemon_service.initialize_database(total=0)

        assert len(result) == 0
        assert isinstance(result, list)
        pokemon_service.repository.create.assert_not_called()

    @staticmethod
    @pytest.mark.asyncio
    async def test_initialize_database_repository_create_error_zero_total(pokemon_service):
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
        pokemon_service.repository.create = AsyncMock(side_effect=Exception('Database error'))

        result = await pokemon_service.initialize_database(total=0)

        assert len(result) == 0
        assert isinstance(result, list)
        pokemon_service.repository.create.assert_called_once()

    @staticmethod
    @pytest.mark.asyncio
    async def test_initialize_database_repository_create_error_with_existing(pokemon_service):
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
        pokemon_service.repository.create = AsyncMock(side_effect=Exception('Database error'))

        result = await pokemon_service.initialize_database(total=1)

        assert len(result) == 0
        assert isinstance(result, list)
        pokemon_service.repository.create.assert_called_once()

    @staticmethod
    @pytest.mark.asyncio
    async def test_initialize_database_empty_external_list(pokemon_service):
        """Should return empty list when external pokemon_service returns no pokemon"""

        pokemon_service.external_service.pokemon_external_list = AsyncMock(return_value=[])
        pokemon_service.repository.create = AsyncMock()

        result = await pokemon_service.initialize_database(total=0)

        assert len(result) == 0
        assert isinstance(result, list)
        pokemon_service.external_service.pokemon_external_list.assert_called_once_with(
            offset=0, limit=1302
        )
        pokemon_service.repository.create.assert_not_called()

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
        pokemon_service.repository.create = AsyncMock(return_value=created_pokemon)

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
    async def test_initialize_database_calls_correct_create_schema(pokemon_service):
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

        pokemon_service.external_service.pokemon_external_list = AsyncMock(
            return_value=[external_pokemon]
        )
        pokemon_service.repository.create = AsyncMock(return_value=created_pokemon)

        await pokemon_service.initialize_database(total=0)

        call_args = pokemon_service.repository.create.call_args
        pokemon_schema = call_args.kwargs['pokemon_data']

        assert pokemon_schema.name == 'Dragonite'
        assert pokemon_schema.order == MOCK_ENTITY_ORDER
        assert pokemon_schema.url == 'https://pokeapi.co/api/v2/pokemon/149'
        assert (
            pokemon_schema.external_image
            == 'https://raw.githubusercontent.com/PokeAPI/sprites/149.png'
        )


class TestPokemonServiceInitialize:
    """Test scope for fetch_all method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_fetch_all_success_with_complete_database(pokemon_service):
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

        pokemon_service.repository.total = AsyncMock(return_value=1302)
        pokemon_service.repository.list_all = AsyncMock(return_value=pokemon_list)

        page_filter = FilterPage(offset=0, limit=10)
        result = await pokemon_service.initialize(page_filter=page_filter)

        assert len(result) == total_list
        assert result[0].name == 'Bulbasaur'
        assert result[1].name == 'Ivysaur'
        pokemon_service.repository.total.assert_called_once()
        pokemon_service.repository.list_all.assert_called_once_with(page_filter=page_filter)

    @staticmethod
    @pytest.mark.asyncio
    async def test_fetch_all_initializes_database_when_incomplete(pokemon_service):
        """Should initialize database and return pokemon when total is less than limit"""
        pokemon_list = [
            SimpleNamespace(
                id=1,
                name='Charizard',
                order=6,
                status=StatusEnum.COMPLETE,
            ),
        ]

        pokemon_service.repository.total = AsyncMock(return_value=100)
        pokemon_service.initialize_database = AsyncMock(return_value=[])
        pokemon_service.repository.list_all = AsyncMock(return_value=pokemon_list)

        page_filter = FilterPage(offset=0, limit=10)
        result = await pokemon_service.initialize(page_filter=page_filter)

        assert len(result) == 1
        assert result[0].name == 'Charizard'
        pokemon_service.repository.total.assert_called_once()
        pokemon_service.initialize_database.assert_called_once_with(total=100)
        pokemon_service.repository.list_all.assert_called_once_with(page_filter=page_filter)

    @staticmethod
    @pytest.mark.asyncio
    async def test_fetch_all_with_offset_and_limit(pokemon_service):
        """Should apply offset and limit filters correctly"""
        pokemon_list = [
            SimpleNamespace(
                id=11,
                name='Pidgeot',
                order=11,
                status=StatusEnum.COMPLETE,
            ),
        ]

        pokemon_service.repository.total = AsyncMock(return_value=1302)
        pokemon_service.repository.list_all = AsyncMock(return_value=pokemon_list)

        page_filter = FilterPage(offset=10, limit=1)
        result = await pokemon_service.initialize(page_filter=page_filter)

        assert len(result) == 1
        assert result[0].name == 'Pidgeot'
        pokemon_service.repository.list_all.assert_called_once_with(page_filter=page_filter)

    @staticmethod
    @pytest.mark.asyncio
    async def test_fetch_all_returns_empty_list_on_error(pokemon_service):
        """Should return empty page when repository raises exception"""

        pokemon_service.repository.total = AsyncMock(side_effect=Exception('Database error'))

        page_filter = FilterPage(offset=0, limit=10)
        result = await pokemon_service.initialize(page_filter=page_filter)

        # Deve retornar LimitOffsetPage vazio com paginação
        assert hasattr(result, 'items')
        assert len(result.items) == 0
        assert result.total == 0

    @staticmethod
    @pytest.mark.asyncio
    async def test_fetch_all_returns_empty_list_on_list_error(pokemon_service):
        """Should return empty page when list query fails"""

        pokemon_service.repository.total = AsyncMock(return_value=1302)
        pokemon_service.repository.list_all = AsyncMock(side_effect=Exception('Query error'))

        page_filter = FilterPage(offset=0, limit=10)
        result = await pokemon_service.initialize(page_filter=page_filter)

        # Deve retornar LimitOffsetPage vazio com paginação
        assert hasattr(result, 'items')
        assert len(result.items) == 0
        assert result.total == 0

    @staticmethod
    @pytest.mark.asyncio
    async def test_fetch_all_returns_empty_list_when_initialization_fails(pokemon_service):
        """Should return empty page when initialize_database fails"""

        pokemon_service.repository.total = AsyncMock(return_value=100)
        pokemon_service.initialize_database = AsyncMock(
            side_effect=Exception('Initialization error')
        )

        page_filter = FilterPage(offset=0, limit=10)
        result = await pokemon_service.initialize(page_filter=page_filter)

        # Deve retornar LimitOffsetPage vazio com paginação
        assert hasattr(result, 'items')
        assert len(result.items) == 0
        assert result.total == 0

    @staticmethod
    @pytest.mark.asyncio
    async def test_fetch_all_empty_result_when_no_pokemon(pokemon_service):
        """Should return empty list when no pokemon exists"""

        pokemon_service.repository.total = AsyncMock(return_value=1302)
        pokemon_service.repository.list_all = AsyncMock(return_value=[])

        page_filter = FilterPage(offset=0, limit=10)
        result = await pokemon_service.initialize(page_filter=page_filter)

        assert result == []
        assert isinstance(result, list)

    @staticmethod
    @pytest.mark.asyncio
    async def test_fetch_all_with_large_offset(pokemon_service):
        """Should handle large offset correctly"""
        pokemon_list = []

        pokemon_service.repository.total = AsyncMock(return_value=1302)
        pokemon_service.repository.list_all = AsyncMock(return_value=pokemon_list)

        page_filter = FilterPage(offset=1300, limit=10)
        result = await pokemon_service.initialize(page_filter=page_filter)

        assert result == []
        pokemon_service.repository.list_all.assert_called_once_with(page_filter=page_filter)

    @staticmethod
    @pytest.mark.asyncio
    async def test_fetch_all_preserves_pokemon_attributes(pokemon_service):
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

        pokemon_service.repository.total = AsyncMock(return_value=1302)
        pokemon_service.repository.list_all = AsyncMock(return_value=pokemon_list)

        page_filter = FilterPage(offset=0, limit=10)
        result = await pokemon_service.initialize(page_filter=page_filter)

        assert len(result) == total_list
        assert result[0].name == 'Pikachu'
        assert result[0].order == MOCK_ENTITY_ORDER
        assert result[0].hp == MOCK_ATTRIBUTES_HP
        assert result[0].attack == MOCK_ATTRIBUTES_ATTACK
        assert result[0].defense == MOCK_ATTRIBUTES_DEFENSE
        assert result[0].speed == MOCK_ATTRIBUTES_SPEED

    @staticmethod
    @pytest.mark.asyncio
    async def test_fetch_all_does_not_initialize_when_total_equals_limit(pokemon_service):
        """Should not call initialize_database when total equals POKEMON_TOTAL_LIMIT"""
        pokemon_list = [
            SimpleNamespace(
                id=1,
                name='Bulbasaur',
                order=1,
                status=StatusEnum.COMPLETE,
            ),
        ]

        pokemon_service.repository.total = AsyncMock(return_value=1302)
        pokemon_service.initialize_database = AsyncMock()
        pokemon_service.repository.list_all = AsyncMock(return_value=pokemon_list)

        page_filter = FilterPage(offset=0, limit=10)
        result = await pokemon_service.initialize(page_filter=page_filter)

        assert len(result) == 1
        pokemon_service.initialize_database.assert_not_called()
        pokemon_service.repository.list_all.assert_called_once()

    @staticmethod
    @pytest.mark.asyncio
    async def test_fetch_all_initializes_when_total_less_than_limit(pokemon_service):
        """Should call initialize_database when total is less than POKEMON_TOTAL_LIMIT"""
        pokemon_list = []

        pokemon_service.repository.total = AsyncMock(return_value=500)
        pokemon_service.initialize_database = AsyncMock(return_value=[])
        pokemon_service.repository.list_all = AsyncMock(return_value=pokemon_list)

        page_filter = FilterPage(offset=0, limit=10)
        result = await pokemon_service.initialize(page_filter=page_filter)

        assert result == []
        pokemon_service.initialize_database.assert_called_once_with(total=500)

    @staticmethod
    @pytest.mark.asyncio
    async def test_fetch_all_with_different_filter_configs(pokemon_service):
        """Should respect different FilterPage configurations"""
        pokemon_list = [SimpleNamespace(name='Venusaur')]
        total_call_count = 3

        pokemon_service.repository.total = AsyncMock(return_value=1302)
        pokemon_service.repository.list_all = AsyncMock(return_value=pokemon_list)

        filters = [
            FilterPage(offset=0, limit=20),
            FilterPage(offset=50, limit=100),
            FilterPage(offset=1200, limit=102),
        ]

        for page_filter in filters:
            result = await pokemon_service.initialize(page_filter=page_filter)
            assert len(result) == 1

        assert pokemon_service.repository.list_all.call_count == total_call_count


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

        pokemon_service.repository.find_one = AsyncMock(return_value=pokemon)

        result = await pokemon_service.fetch_one(name='pikachu')

        assert result is not None
        assert result.name == 'pikachu'
        assert result.status == StatusEnum.COMPLETE
        pokemon_service.repository.find_one.assert_called_once_with(name='pikachu')

    @staticmethod
    @pytest.mark.asyncio
    async def test_fetch_one_not_found_raises_exception(pokemon_service):
        """Should raise HTTPException when pokemon not found"""

        pokemon_service.repository.find_one = AsyncMock(return_value=None)

        with pytest.raises(HTTPException) as exc_info:
            await pokemon_service.fetch_one(name='nonexistent')

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

        pokemon_service.repository.find_one = AsyncMock(return_value=incomplete_pokemon)
        pokemon_service.complete_pokemon_data = AsyncMock(return_value=completed_pokemon)

        result = await pokemon_service.fetch_one(name='bulbasaur')

        assert result is not None
        assert result.status == StatusEnum.COMPLETE
        pokemon_service.complete_pokemon_data.assert_called_once()


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

        pokemon_service.repository.find_one = AsyncMock(return_value=pokemon)

        result = await pokemon_service.validate_entity(pokemon_name='charizard')

        assert result.name == 'charizard'
        assert result.status == StatusEnum.COMPLETE
        pokemon_service.repository.find_one.assert_called_once_with(name='charizard')

    @staticmethod
    @pytest.mark.asyncio
    async def test_validate_entity_not_found_raises_exception(pokemon_service):
        """Should raise HTTPException when pokemon not found"""

        pokemon_service.repository.find_one = AsyncMock(return_value=None)

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

        pokemon_service.repository.find_one = AsyncMock(return_value=incomplete_pokemon)
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

        pokemon_service.repository.find_one = AsyncMock(return_value=incomplete_pokemon)
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

        relationships = GeneratePokemonRelationshipSchema(
            moves=[],
            types=[],
            abilities=[],
            growth_rate=PokemonExternalBase(
                url='https://pokeapi.co/api/v2/growth-rate/medium-slow/', name='medium-slow'
            ),
        )

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

        pokemon_service.external_service.fetch_by_name = AsyncMock(return_value=external_data)
        pokemon_service.generate_relationships = AsyncMock(return_value=relationships)
        pokemon_service.add_evolutions = AsyncMock(return_value=evolutions)
        pokemon_service.business.merge_if_changed = MagicMock(return_value=updated_pokemon)
        pokemon_service.repository.update = AsyncMock()
        pokemon_service.repository.find_one = AsyncMock(return_value=updated_pokemon)

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
        pokemon_service.repository.find_one.assert_called_once_with(name='bulbasaur')

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
        pokemon_service.repository.find_one = AsyncMock(return_value=updated_pokemon)

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


class TestPokemonServiceListAll:
    """Test scope for list_all method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_list_all_returns_repository_results(pokemon_service):
        """Should return repository list when no error occurs"""
        pokemon_list = [SimpleNamespace(name='Bulbasaur')]
        pokemon_service.repository.list_all = AsyncMock(return_value=pokemon_list)

        page_filter = FilterPage(offset=LIST_OFFSET, limit=LIST_LIMIT)
        result = await pokemon_service.list_all(page_filter=page_filter)

        assert result == pokemon_list
        pokemon_service.repository.list_all.assert_called_once_with(page_filter=page_filter)

    @staticmethod
    @pytest.mark.asyncio
    async def test_list_all_returns_empty_page_on_error_with_pagination(pokemon_service):
        """Should return empty page when repository raises and pagination is set"""
        pokemon_service.repository.list_all = AsyncMock(side_effect=Exception('boom'))

        page_filter = FilterPage(offset=LIST_OFFSET, limit=LIST_LIMIT)
        result = await pokemon_service.list_all(page_filter=page_filter)

        assert hasattr(result, 'items')
        assert len(result.items) == 0
        assert result.total == 0

    @staticmethod
    @pytest.mark.asyncio
    async def test_list_all_returns_empty_list_on_error_without_pagination(
        pokemon_service,
    ):
        """Should return empty list when repository raises without pagination"""
        pokemon_service.repository.list_all = AsyncMock(side_effect=Exception('boom'))

        result = await pokemon_service.list_all(page_filter=None)

        assert result == []


class TestPokemonServiceTotal:
    """Test scope for total method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_total_returns_repository_total(pokemon_service):
        """Should return repository total"""
        pokemon_service.repository.total = AsyncMock(return_value=TOTAL_COUNT)

        result = await pokemon_service.total()

        assert result == TOTAL_COUNT
        pokemon_service.repository.total.assert_awaited_once()
