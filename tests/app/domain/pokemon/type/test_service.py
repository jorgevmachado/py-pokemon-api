from unittest.mock import AsyncMock, patch

import pytest

from app.domain.pokemon.external.schemas import (
    PokemonExternalBase,
    PokemonExternalBaseTypeSchemaResponse,
    PokemonExternalTypeDamageRelationsSchemaResponse,
    PokemonExternalTypeSchemaResponse,
)
from app.domain.pokemon.type.business import PokemonTypeBusiness, TypeColor
from app.domain.pokemon.type.service import PokemonTypeService
from app.models import PokemonType

MOCK_RESULT_ORDER = 10


class TestPokemonTypeServiceVerifyPokemonType:
    """Test scope for verify_pokemon_type method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_verify_pokemon_type_in_database_success(session):
        total_results = 1
        pokemon_type = PokemonType(
            url='https://pokeapi.co/api/v2/type/12/',
            name='fire',
            order=total_results,
            text_color='#fff',
            background_color='#fd7d24',
        )
        response_pokemon_type = PokemonExternalBaseTypeSchemaResponse(
            slot=1,
            type=PokemonExternalBase(name='ice', url='https://pokeapi.co/api/v2/type/12/'),
        )

        service = PokemonTypeService(session=session)
        service.repository.find_one_by_order = AsyncMock(return_value=pokemon_type)
        result = await service.verify_pokemon_type(types=[response_pokemon_type])

        assert len(result) == total_results
        assert result[0].name == 'fire'
        assert result[0].order == 1
        assert result[0].text_color == '#fff'
        assert result[0].background_color == '#fd7d24'
        service.repository.find_one_by_order.assert_called_once()

    @staticmethod
    @pytest.mark.asyncio
    async def test_verify_pokemon_type_not_in_database_success(session):
        total_results = 1
        service = PokemonTypeService(session=session)
        pokemon_type_order = 12
        response_pokemon_type = PokemonExternalBaseTypeSchemaResponse(
            slot=1,
            type=PokemonExternalBase(
                name='fire', url=f'https://pokeapi.co/api/v2/type/{pokemon_type_order}/'
            ),
        )

        created_pokemon_type = PokemonType(
            url=f'https://pokeapi.co/api/v2/type/{pokemon_type_order}/',
            name='fire',
            order=pokemon_type_order,
            text_color='#fff',
            background_color='#fd7d24',
        )

        type_color = TypeColor(
            id=3, name='fire', text_color='#fff', background_color='#fd7d24'
        )

        with patch.object(
            PokemonTypeBusiness,
            'ensure_colors',
            return_value=type_color,
        ):
            service.repository.find_one_by_order = AsyncMock(return_value=None)
            service.repository.find_one = AsyncMock(return_value=None)
            service.repository.create = AsyncMock(return_value=created_pokemon_type)
            result = await service.verify_pokemon_type(types=[response_pokemon_type])
        total_call_count = 2
        assert len(result) == total_results
        assert result[0].name == 'fire'
        assert result[0].order == pokemon_type_order
        assert result[0].text_color == '#fff'
        assert result[0].background_color == '#fd7d24'
        assert service.repository.find_one_by_order.call_count == total_call_count
        service.repository.find_one.assert_called_once()
        service.repository.create.assert_called_once()

    @staticmethod
    @pytest.mark.asyncio
    async def test_verify_pokemon_type_error(session):
        service = PokemonTypeService(session=session)

        response_pokemon_type = PokemonExternalBaseTypeSchemaResponse(
            slot=1,
            type=PokemonExternalBase(name='fire', url='https://pokeapi.co/api/v2/type/12/'),
        )
        service.repository.find_one_by_order = AsyncMock(
            side_effect=Exception('Database error')
        )

        result = await service.verify_pokemon_type(types=[response_pokemon_type])
        assert len(result) == 0
        service.repository.find_one_by_order.assert_called_once()


class TestPokemonTypeServicePersist:
    """Test scope for persist method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_persist_existing_type_by_order(session):
        """Should return existing pokemon type when found by order"""
        pokemon_type = PokemonType(
            url='https://pokeapi.co/api/v2/type/10/',
            name='fire',
            order=MOCK_RESULT_ORDER,
            text_color='#fff',
            background_color='#fd7d24',
        )

        service = PokemonTypeService(session=session)
        service.repository.find_one_by_order = AsyncMock(return_value=pokemon_type)

        external_base = PokemonExternalBase(
            name='fire', url='https://pokeapi.co/api/v2/type/10/'
        )
        result = await service.persist(pokemon_type=external_base, with_damage_relations=False)

        assert result.name == 'fire'
        assert result.order == MOCK_RESULT_ORDER
        service.repository.find_one_by_order.assert_called_once()

    @staticmethod
    @pytest.mark.asyncio
    async def test_persist_existing_type_by_name(session):
        """Should return existing pokemon type when found by name"""
        pokemon_type = PokemonType(
            url='https://pokeapi.co/api/v2/type/10/',
            name='fire',
            order=MOCK_RESULT_ORDER,
            text_color='#fff',
            background_color='#fd7d24',
        )

        service = PokemonTypeService(session=session)
        service.repository.find_one_by_order = AsyncMock(return_value=None)
        service.repository.find_one = AsyncMock(return_value=pokemon_type)

        external_base = PokemonExternalBase(
            name='fire', url='https://pokeapi.co/api/v2/type/10/'
        )
        result = await service.persist(pokemon_type=external_base, with_damage_relations=False)

        assert result.name == 'fire'
        assert result.order == MOCK_RESULT_ORDER
        service.repository.find_one_by_order.assert_called_once()
        service.repository.find_one.assert_called_once()

    @staticmethod
    @pytest.mark.asyncio
    async def test_persist_new_type(session):
        """Should create new pokemon type when not found"""
        type_color = TypeColor(
            id=3, name='fire', text_color='#fff', background_color='#fd7d24'
        )

        created_pokemon_type = PokemonType(
            url='https://pokeapi.co/api/v2/type/10/',
            name='fire',
            order=MOCK_RESULT_ORDER,
            text_color='#fff',
            background_color='#fd7d24',
        )

        service = PokemonTypeService(session=session)
        service.repository.find_one_by_order = AsyncMock(return_value=None)
        service.repository.find_one = AsyncMock(return_value=None)
        service.repository.create = AsyncMock(return_value=created_pokemon_type)

        with patch.object(PokemonTypeBusiness, 'ensure_colors', return_value=type_color):
            external_base = PokemonExternalBase(
                name='fire', url='https://pokeapi.co/api/v2/type/10/'
            )
            result = await service.persist(
                pokemon_type=external_base, with_damage_relations=False
            )

        assert result.name == 'fire'
        assert result.order == MOCK_RESULT_ORDER
        assert result.text_color == '#fff'
        assert result.background_color == '#fd7d24'
        service.repository.create.assert_called_once()

    @staticmethod
    @pytest.mark.asyncio
    async def test_persist_existing_type_updates_damage_relations(session):
        """Should update existing pokemon type with damage relations when missing"""
        pokemon_type = PokemonType(
            url='https://pokeapi.co/api/v2/type/10/',
            name='fire',
            order=MOCK_RESULT_ORDER,
            text_color='#fff',
            background_color='#fd7d24',
        )
        weakness_type = PokemonType(
            url='https://pokeapi.co/api/v2/type/11/',
            name='water',
            order=11,
            text_color='#fff',
            background_color='#4592c4',
        )
        strength_type = PokemonType(
            url='https://pokeapi.co/api/v2/type/12/',
            name='grass',
            order=12,
            text_color='#fff',
            background_color='#9bcc50',
        )

        service = PokemonTypeService(session=session)
        service.repository.find_one_by_order = AsyncMock(return_value=pokemon_type)
        service.repository.update = AsyncMock(return_value=pokemon_type)
        service.validate_damage_relations = AsyncMock(
            return_value=type(
                'DamageResult',
                (),
                {'weaknesses': [weakness_type], 'strengths': [strength_type]},
            )()
        )

        external_base = PokemonExternalBase(
            name='fire', url='https://pokeapi.co/api/v2/type/10/'
        )
        result = await service.persist(pokemon_type=external_base, with_damage_relations=True)

        assert result.weaknesses == [weakness_type]
        assert result.strengths == [strength_type]
        service.repository.find_one_by_order.assert_called_once()
        service.validate_damage_relations.assert_called_once()
        service.repository.update.assert_called_once()


class TestPokemonTypeServiceValidateDamageRelations:
    """Test scope for validate_damage_relations method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_validate_damage_relations_success(session):
        """Should return damage relations when external API returns data"""
        damage_relations = PokemonExternalTypeDamageRelationsSchemaResponse(
            double_damage_from=[
                PokemonExternalBase(name='water', url='https://pokeapi.co/api/v2/type/11/')
            ],
            double_damage_to=[
                PokemonExternalBase(name='grass', url='https://pokeapi.co/api/v2/type/12/')
            ],
            half_damage_from=[],
            half_damage_to=[],
        )
        external_type = PokemonExternalTypeSchemaResponse(
            id=MOCK_RESULT_ORDER,
            damage_relations=damage_relations,
            game_indices=[],
            generation=PokemonExternalBase(
                name='generation-i', url='https://pokeapi.co/api/v2/generation/1/'
            ),
            move_damage_class=PokemonExternalBase(
                name='special', url='https://pokeapi.co/api/v2/move-damage-class/2/'
            ),
            moves=[],
            names=[],
        )

        service = PokemonTypeService(session=session)
        service.external_service.pokemon_external_type_by_url = AsyncMock(
            return_value=external_type
        )
        service.repository.find_one_by_order = AsyncMock(return_value=None)
        service.repository.find_one = AsyncMock(return_value=None)

        type_color = TypeColor(
            id=3, name='fire', text_color='#fff', background_color='#fd7d24'
        )

        with patch.object(PokemonTypeBusiness, 'ensure_colors', return_value=type_color):
            result = await service.validate_damage_relations(
                url='https://pokeapi.co/api/v2/type/10/'
            )

        assert len(result.weaknesses) == 1
        assert len(result.strengths) == 1

    @staticmethod
    @pytest.mark.asyncio
    async def test_validate_damage_relations_no_external_data(session):
        """Should return empty relations when external API returns None"""
        service = PokemonTypeService(session=session)
        service.external_service.pokemon_external_type_by_url = AsyncMock(return_value=None)

        result = await service.validate_damage_relations(
            url='https://pokeapi.co/api/v2/type/10/'
        )

        assert len(result.weaknesses) == 0
        assert len(result.strengths) == 0
