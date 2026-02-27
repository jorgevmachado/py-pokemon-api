from unittest.mock import AsyncMock

import pytest

from app.domain.pokemon.move.repository import PokemonMoveRepository
from app.domain.pokemon.move.schema import CreatePokemonMoveSchema
from app.models import PokemonMove

MOCK_POKEMON_MOVE_PP = 35
MOCK_POKEMON_MOVE_POWER = 40
MOCK_POKEMON_MOVE_ACCURACY = 100
MOCK_POKEMON_MOVE_PRIORITY = 0


class TestPokemonMoveRepositoryCreate:
    """Test scope for create method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_move_repository_create_success(session):
        """Should persist pokemon move when data is valid"""
        pokemon_move_data_order = 1
        pokemon_move_data = CreatePokemonMoveSchema(
            url='https://pokeapi.co/api/v2/move/1/',
            name='pound',
            order=pokemon_move_data_order,
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
        repository = PokemonMoveRepository(session=session)
        pokemon_move = await repository.create(pokemon_move_data)

        assert pokemon_move.url == 'https://pokeapi.co/api/v2/move/1/'
        assert pokemon_move.name == 'pound'
        assert pokemon_move.order == pokemon_move_data_order
        assert pokemon_move.type == 'normal'
        assert pokemon_move.power == MOCK_POKEMON_MOVE_POWER
        assert pokemon_move.pp == MOCK_POKEMON_MOVE_PP
        assert pokemon_move.accuracy == MOCK_POKEMON_MOVE_ACCURACY
        assert pokemon_move.priority == MOCK_POKEMON_MOVE_PRIORITY
        assert pokemon_move.target == 'single-target'
        assert pokemon_move.damage_class == 'physical'
        assert pokemon_move.effect == 'Inflicts regular damage.'
        assert pokemon_move.short_effect == 'Deals regular damage.'
        assert pokemon_move.effect_chance is None

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_move_repository_create_commit_error(session):
        """Should raise exception when database commit fails"""
        pokemon_move_data = CreatePokemonMoveSchema(
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
        session.commit = AsyncMock(side_effect=Exception('Database error'))

        repository = PokemonMoveRepository(session=session)

        with pytest.raises(Exception, match='Database error'):
            await repository.create(pokemon_move_data)


class TestPokemonMoveRepositoryFindOneByOrder:
    """Test scope for find one by order method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_move_repository_find_one_not_found(session):
        """Should return None when pokemon move is not found"""
        repository = PokemonMoveRepository(session=session)
        result = await repository.find_one_by_order(999)

        assert result is None

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_move_repository_find_one_by_order_success(session):
        """Should return pokemon move when found by order"""
        result_order = 1

        pokemon_move = PokemonMove(
            url='https://pokeapi.co/api/v2/move/1/',
            name='pound',
            order=result_order,
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
        session.add(pokemon_move)
        await session.commit()

        repository = PokemonMoveRepository(session=session)
        result = await repository.find_one_by_order(result_order)

        assert result is not None
        assert isinstance(result, PokemonMove)
        assert result.order == result_order
        assert result.name == 'pound'
        assert result.type == 'normal'
