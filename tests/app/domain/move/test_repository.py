from unittest.mock import AsyncMock

import pytest

from app.models.pokemon_move import PokemonMove

MOCK_POKEMON_MOVE_PP = 35
MOCK_POKEMON_MOVE_POWER = 40
MOCK_POKEMON_MOVE_ACCURACY = 100
MOCK_POKEMON_MOVE_PRIORITY = 0


class TestPokemonMoveRepositorySave:
    """Test scope for save method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_move_repository_save_success(pokemon_move_repository):
        """Should persist pokemon move when data is valid"""
        pokemon_move_data_order = 1

        pokemon_move = await pokemon_move_repository.save(
            entity=PokemonMove(
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
        )

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
    async def test_pokemon_move_repository_save_commit_error(session, pokemon_move_repository):
        """Should raise exception when database commit fails"""
        session.commit = AsyncMock(side_effect=Exception('Database error'))

        with pytest.raises(Exception, match='Database error'):
            await pokemon_move_repository.save(
                entity=PokemonMove(
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
            )


class TestPokemonMoveRepositoryFindBy:
    """Test scope for find by method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_move_repository_find_by_not_found(pokemon_move_repository):
        """Should return None when pokemon move is not found"""
        result = await pokemon_move_repository.find_by(order=999)

        assert result is None

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_move_repository_find_by_order_success(
        pokemon_move, pokemon_move_repository
    ):
        """Should return pokemon move when found by order"""
        result = await pokemon_move_repository.find_by(order=pokemon_move.order)

        assert result is not None
        assert isinstance(result, PokemonMove)
        assert result.order == pokemon_move.order
        assert result.name == pokemon_move.name
        assert result.type == pokemon_move.type
