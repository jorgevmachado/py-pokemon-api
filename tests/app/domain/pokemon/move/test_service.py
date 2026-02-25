from unittest.mock import AsyncMock, patch

import pytest

from app.domain.pokemon.external.schemas import (
    PokemonExternalBase,
    PokemonExternalBaseMoveSchemaResponse,
)
from app.domain.pokemon.move.business import EffectEntry, PokemonMoveBusiness
from app.domain.pokemon.move.service import PokemonMoveService
from app.models import PokemonMove

MOCK_POKEMON_MOVE_POWER = 40
MOCK_POKEMON_MOVE_PP = 35
MOCK_POKEMON_MOVE_ACCURACY = 100
MOCK_POKEMON_MOVE_PRIORITY = 0
MOCK_POKEMON_MOVE_KARATE_CHOP_POWER = 50
MOCK_POKEMON_MOVE_KARATE_CHOP_PP = 25
TOTAL_MOVES_MULTIPLE = 2


class TestPokemonMoveServiceVerifyPokemonMove:
    """Test scope for verify_pokemon_move method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_verify_pokemon_move_in_database_success(session):
        """Should return pokemon move from database when it exists"""
        total_results = 1
        pokemon_move = PokemonMove(
            url='https://pokeapi.co/api/v2/move/1/',
            name='pound',
            order=1,
            type='normal',
            power=MOCK_POKEMON_MOVE_POWER,
            pp=MOCK_POKEMON_MOVE_PP,
            accuracy=MOCK_POKEMON_MOVE_ACCURACY,
            priority=MOCK_POKEMON_MOVE_PRIORITY,
            target='single-target',
            damage_class='physical',
            effect='Inflicts regular damage.',
            short_effect='Deals regular damage.',
            effect_chance=None,
        )
        response_pokemon_move = PokemonExternalBaseMoveSchemaResponse(
            move=PokemonExternalBase(name='pound', url='https://pokeapi.co/api/v2/move/1/')
        )

        service = PokemonMoveService(session=session)
        service.repository.find_one_by_order = AsyncMock(return_value=pokemon_move)
        result = await service.verify_pokemon_move(moves=[response_pokemon_move])

        assert len(result) == total_results
        assert result[0].name == 'pound'
        assert result[0].order == 1
        assert result[0].type == 'normal'
        assert result[0].power == MOCK_POKEMON_MOVE_POWER
        assert result[0].pp == MOCK_POKEMON_MOVE_PP
        service.repository.find_one_by_order.assert_called_once()

    @staticmethod
    @pytest.mark.asyncio
    async def test_verify_pokemon_move_not_in_database_success(session):
        """Should create and return pokemon move when it does not exist in database"""
        total_results = 1
        service = PokemonMoveService(session=session)
        pokemon_move_order = 1
        response_pokemon_move = PokemonExternalBaseMoveSchemaResponse(
            move=PokemonExternalBase(
                name='pound', url=f'https://pokeapi.co/api/v2/move/{pokemon_move_order}/'
            )
        )

        effect_entry = EffectEntry(
            effect='Inflicts regular damage.',
            short_effect='Deals regular damage.',
        )

        external_move_data = AsyncMock()
        external_move_data.pp = MOCK_POKEMON_MOVE_PP
        external_move_data.power = MOCK_POKEMON_MOVE_POWER
        external_move_data.accuracy = MOCK_POKEMON_MOVE_ACCURACY
        external_move_data.priority = MOCK_POKEMON_MOVE_PRIORITY
        external_move_data.type = PokemonExternalBase(
            name='normal', url='https://pokeapi.co/api/v2/type/1/'
        )
        external_move_data.target = PokemonExternalBase(
            name='single-target', url='https://pokeapi.co/api/v2/move-target/1/'
        )
        external_move_data.damage_class = PokemonExternalBase(
            name='physical', url='https://pokeapi.co/api/v2/move-damage-class/1/'
        )
        external_move_data.name = 'pound'
        external_move_data.effect_entries = []
        external_move_data.effect_chance = None

        pokemon_move = PokemonMove(
            url='https://pokeapi.co/api/v2/move/1/',
            name='pound',
            order=pokemon_move_order,
            type='normal',
            power=MOCK_POKEMON_MOVE_POWER,
            pp=MOCK_POKEMON_MOVE_PP,
            accuracy=MOCK_POKEMON_MOVE_ACCURACY,
            priority=MOCK_POKEMON_MOVE_PRIORITY,
            target='single-target',
            damage_class='physical',
            effect='Inflicts regular damage.',
            short_effect='Deals regular damage.',
            effect_chance=None,
        )

        service.repository.find_one_by_order = AsyncMock(return_value=None)
        service.repository.create = AsyncMock(return_value=pokemon_move)

        with patch.object(
            PokemonMoveBusiness,
            'ensure_effect_message',
            return_value=effect_entry,
        ):
            with patch.object(
                service.external_service,
                'pokemon_external_move_by_name',
                return_value=external_move_data,
            ):
                result = await service.verify_pokemon_move(moves=[response_pokemon_move])

        assert len(result) == total_results
        assert result[0].name == 'pound'
        assert result[0].order == pokemon_move_order
        assert result[0].type == 'normal'
        assert result[0].power == MOCK_POKEMON_MOVE_POWER
        service.repository.find_one_by_order.assert_called_once()
        service.repository.create.assert_called_once()

    @staticmethod
    @pytest.mark.asyncio
    async def test_verify_pokemon_move_external_service_no_data(session):
        """Should skip move when external service returns no data"""
        service = PokemonMoveService(session=session)
        response_pokemon_move = PokemonExternalBaseMoveSchemaResponse(
            move=PokemonExternalBase(
                name='unknown-move', url='https://pokeapi.co/api/v2/move/999/'
            )
        )

        service.repository.find_one_by_order = AsyncMock(return_value=None)

        with patch.object(
            service.external_service,
            'pokemon_external_move_by_name',
            return_value=None,
        ):
            result = await service.verify_pokemon_move(moves=[response_pokemon_move])

        assert len(result) == 0
        service.repository.find_one_by_order.assert_called_once()

    @staticmethod
    @pytest.mark.asyncio
    async def test_verify_pokemon_move_empty_list(session):
        """Should return empty list when moves list is empty"""
        service = PokemonMoveService(session=session)
        service.repository.find_one_by_order = AsyncMock()
        result = await service.verify_pokemon_move(moves=[])

        assert len(result) == 0
        service.repository.find_one_by_order.assert_not_called()

    @staticmethod
    @pytest.mark.asyncio
    async def test_verify_pokemon_move_multiple_moves(session):
        """Should process multiple moves correctly"""
        service = PokemonMoveService(session=session)

        pokemon_move_1 = PokemonMove(
            url='https://pokeapi.co/api/v2/move/1/',
            name='pound',
            order=1,
            type='normal',
            power=MOCK_POKEMON_MOVE_POWER,
            pp=MOCK_POKEMON_MOVE_PP,
            accuracy=MOCK_POKEMON_MOVE_ACCURACY,
            priority=MOCK_POKEMON_MOVE_PRIORITY,
            target='single-target',
            damage_class='physical',
            effect='Inflicts regular damage.',
            short_effect='Deals regular damage.',
            effect_chance=None,
        )

        pokemon_move_2 = PokemonMove(
            url='https://pokeapi.co/api/v2/move/2/',
            name='karate-chop',
            order=2,
            type='fighting',
            power=MOCK_POKEMON_MOVE_KARATE_CHOP_POWER,
            pp=MOCK_POKEMON_MOVE_KARATE_CHOP_PP,
            accuracy=MOCK_POKEMON_MOVE_ACCURACY,
            priority=MOCK_POKEMON_MOVE_PRIORITY,
            target='single-target',
            damage_class='physical',
            effect='High critical hit ratio.',
            short_effect='High critical hit ratio.',
            effect_chance=None,
        )

        response_moves = [
            PokemonExternalBaseMoveSchemaResponse(
                move=PokemonExternalBase(name='pound', url='https://pokeapi.co/api/v2/move/1/')
            ),
            PokemonExternalBaseMoveSchemaResponse(
                move=PokemonExternalBase(
                    name='karate-chop', url='https://pokeapi.co/api/v2/move/2/'
                )
            ),
        ]

        service.repository.find_one_by_order = AsyncMock(
            side_effect=[pokemon_move_1, pokemon_move_2]
        )

        result = await service.verify_pokemon_move(moves=response_moves)

        assert len(result) == TOTAL_MOVES_MULTIPLE
        assert result[0].name == 'pound'
        assert result[1].name == 'karate-chop'
        assert service.repository.find_one_by_order.call_count == TOTAL_MOVES_MULTIPLE
