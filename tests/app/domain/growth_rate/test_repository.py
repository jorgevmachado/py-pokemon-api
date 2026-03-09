from unittest.mock import AsyncMock

import pytest

from app.domain.growth_rate.model import PokemonGrowthRate
from app.domain.growth_rate.repository import PokemonGrowthRateRepository
from app.domain.growth_rate.schema import CreatePokemonGrowthRateSchema

MOCK_GROWTH_RATE_ORDER = 1
MOCK_GROWTH_RATE_ORDER_2 = 2


class TestPokemonGrowthRateRepositoryCreate:
    """Test scope for create method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_growth_rate_repository_create_success(session):
        """Should persist pokemon growth rate when data is valid"""
        pokemon_growth_rate_data = CreatePokemonGrowthRateSchema(
            url='https://pokeapi.co/api/v2/growth-rate/1/',
            name='slow',
            order=MOCK_GROWTH_RATE_ORDER,
            formula='\\frac{5x^3}{4}',
            description='',
        )
        repository = PokemonGrowthRateRepository(session=session)
        pokemon_growth_rate = await repository.create(pokemon_growth_rate_data)

        assert pokemon_growth_rate.url == 'https://pokeapi.co/api/v2/growth-rate/1/'
        assert pokemon_growth_rate.name == 'slow'
        assert pokemon_growth_rate.order == MOCK_GROWTH_RATE_ORDER
        assert pokemon_growth_rate.formula == '\\frac{5x^3}{4}'

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_growth_rate_repository_create_with_complex_formula(session):
        """Should persist pokemon growth rate with complex formula when valid"""
        pokemon_growth_rate_data = CreatePokemonGrowthRateSchema(
            url='https://pokeapi.co/api/v2/growth-rate/2/',
            name='medium',
            order=MOCK_GROWTH_RATE_ORDER_2,
            formula='x^3',
            description='',
        )
        repository = PokemonGrowthRateRepository(session=session)
        pokemon_growth_rate = await repository.create(pokemon_growth_rate_data)

        assert pokemon_growth_rate.url == 'https://pokeapi.co/api/v2/growth-rate/2/'
        assert pokemon_growth_rate.name == 'medium'
        assert pokemon_growth_rate.order == MOCK_GROWTH_RATE_ORDER_2
        assert pokemon_growth_rate.formula == 'x^3'

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_growth_rate_repository_create_commit_error(session):
        """Should raise exception when database commit fails"""
        pokemon_growth_rate_data = CreatePokemonGrowthRateSchema(
            url='https://pokeapi.co/api/v2/growth-rate/1/',
            name='slow',
            order=MOCK_GROWTH_RATE_ORDER,
            formula='\\frac{5x^3}{4}',
            description='',
        )
        session.commit = AsyncMock(side_effect=Exception('Database error'))

        repository = PokemonGrowthRateRepository(session=session)

        with pytest.raises(Exception, match='Database error'):
            await repository.create(pokemon_growth_rate_data)


class TestPokemonGrowthRateRepositoryFindOneByOrder:
    """Test scope for find one by order method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_growth_rate_repository_find_one_not_found(session):
        """Should return None when pokemon growth rate is not found"""
        repository = PokemonGrowthRateRepository(session=session)
        result = await repository.find_one_by_order(999)

        assert result is None

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_growth_rate_repository_find_one_by_order_success(session):
        """Should return pokemon growth rate when found by order"""
        pokemon_growth_rate = PokemonGrowthRate(
            url='https://pokeapi.co/api/v2/growth-rate/1/',
            name='slow',
            order=MOCK_GROWTH_RATE_ORDER,
            formula='\\frac{5x^3}{4}',
        )
        session.add(pokemon_growth_rate)
        await session.commit()

        repository = PokemonGrowthRateRepository(session=session)
        result = await repository.find_one_by_order(MOCK_GROWTH_RATE_ORDER)

        assert result is not None
        assert isinstance(result, PokemonGrowthRate)
        assert result.order == MOCK_GROWTH_RATE_ORDER
        assert result.name == 'slow'
        assert result.formula == '\\frac{5x^3}{4}'

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_growth_rate_repository_find_one_by_order_medium(session):
        """Should return medium growth rate when found by order"""
        pokemon_growth_rate = PokemonGrowthRate(
            url='https://pokeapi.co/api/v2/growth-rate/2/',
            name='medium',
            order=MOCK_GROWTH_RATE_ORDER_2,
            formula='x^3',
        )
        session.add(pokemon_growth_rate)
        await session.commit()

        repository = PokemonGrowthRateRepository(session=session)
        result = await repository.find_one_by_order(MOCK_GROWTH_RATE_ORDER_2)

        assert result is not None
        assert isinstance(result, PokemonGrowthRate)
        assert result.order == MOCK_GROWTH_RATE_ORDER_2
        assert result.name == 'medium'
        assert result.formula == 'x^3'
