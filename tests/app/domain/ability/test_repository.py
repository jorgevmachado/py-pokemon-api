from unittest.mock import AsyncMock

import pytest

from app.domain.ability.model import PokemonAbility
from app.domain.ability.schema import CreatePokemonAbilitySchema

MOCK_POKEMON_ABILITY_SLOT = 1
MOCK_POKEMON_ABILITY_SLOT_2 = 2
MOCK_POKEMON_ABILITY_IS_HIDDEN = False


class TestPokemonAbilityRepositoryCreate:
    """Test scope for create method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_ability_repository_create_success(pokemon_ability_repository):
        """Should persist pokemon ability when data is valid"""
        pokemon_ability_data_order = 1
        pokemon_ability_data = CreatePokemonAbilitySchema(
            url='https://pokeapi.co/api/v2/ability/1/',
            name='stench',
            order=pokemon_ability_data_order,
            slot=MOCK_POKEMON_ABILITY_SLOT,
            is_hidden=MOCK_POKEMON_ABILITY_IS_HIDDEN,
        )
        pokemon_ability = await pokemon_ability_repository.create(pokemon_ability_data)

        assert pokemon_ability.url == 'https://pokeapi.co/api/v2/ability/1/'
        assert pokemon_ability.name == 'stench'
        assert pokemon_ability.order == pokemon_ability_data_order
        assert pokemon_ability.slot == MOCK_POKEMON_ABILITY_SLOT
        assert pokemon_ability.is_hidden is MOCK_POKEMON_ABILITY_IS_HIDDEN

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_ability_repository_create_with_hidden_ability(
        pokemon_ability_repository,
    ):
        """Should persist pokemon ability with hidden flag when data is valid"""
        pokemon_ability_data_order = MOCK_POKEMON_ABILITY_SLOT_2
        pokemon_ability_data = CreatePokemonAbilitySchema(
            url='https://pokeapi.co/api/v2/ability/2/',
            name='static',
            order=pokemon_ability_data_order,
            slot=MOCK_POKEMON_ABILITY_SLOT_2,
            is_hidden=True,
        )

        pokemon_ability = await pokemon_ability_repository.create(pokemon_ability_data)

        assert pokemon_ability.url == 'https://pokeapi.co/api/v2/ability/2/'
        assert pokemon_ability.name == 'static'
        assert pokemon_ability.order == pokemon_ability_data_order
        assert pokemon_ability.slot == MOCK_POKEMON_ABILITY_SLOT_2
        assert pokemon_ability.is_hidden is True

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_ability_repository_create_commit_error(
        pokemon_ability_repository, session
    ):
        """Should raise exception when database commit fails"""
        pokemon_ability_data = CreatePokemonAbilitySchema(
            url='https://pokeapi.co/api/v2/ability/1/',
            name='stench',
            order=1,
            slot=MOCK_POKEMON_ABILITY_SLOT,
            is_hidden=MOCK_POKEMON_ABILITY_IS_HIDDEN,
        )
        session.commit = AsyncMock(side_effect=Exception('Database error'))

        with pytest.raises(Exception, match='Database error'):
            await pokemon_ability_repository.create(pokemon_ability_data)


class TestPokemonAbilityRepositoryFindOneByOrder:
    """Test scope for find one by order method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_ability_repository_find_one_not_found(pokemon_ability_repository):
        """Should return None when pokemon ability is not found"""

        result = await pokemon_ability_repository.find_one_by_order(999)

        assert result is None

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_ability_repository_find_one_by_order_success(
        pokemon_ability_repository, session
    ):
        """Should return pokemon ability when found by order"""
        result_order = 1

        pokemon_ability = PokemonAbility(
            url='https://pokeapi.co/api/v2/ability/1/',
            name='stench',
            order=result_order,
            slot=MOCK_POKEMON_ABILITY_SLOT,
            is_hidden=MOCK_POKEMON_ABILITY_IS_HIDDEN,
        )
        session.add(pokemon_ability)
        await session.commit()

        result = await pokemon_ability_repository.find_one_by_order(result_order)

        assert result is not None
        assert isinstance(result, PokemonAbility)
        assert result.order == result_order
        assert result.name == 'stench'
        assert result.slot == MOCK_POKEMON_ABILITY_SLOT
        assert result.is_hidden is MOCK_POKEMON_ABILITY_IS_HIDDEN

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_ability_repository_find_one_by_order_hidden(
        pokemon_ability_repository, session
    ):
        """Should return hidden pokemon ability when found by order"""
        result_order = MOCK_POKEMON_ABILITY_SLOT_2

        pokemon_ability = PokemonAbility(
            url='https://pokeapi.co/api/v2/ability/2/',
            name='static',
            order=result_order,
            slot=MOCK_POKEMON_ABILITY_SLOT_2,
            is_hidden=True,
        )
        session.add(pokemon_ability)
        await session.commit()

        result = await pokemon_ability_repository.find_one_by_order(result_order)

        assert result is not None
        assert isinstance(result, PokemonAbility)
        assert result.order == result_order
        assert result.name == 'static'
        assert result.slot == MOCK_POKEMON_ABILITY_SLOT_2
        assert result.is_hidden is True
