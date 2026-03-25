from unittest.mock import AsyncMock

import pytest

from app.models.pokemon_growth_rate import PokemonGrowthRate

MOCK_GROWTH_RATE_ORDER = 1
MOCK_GROWTH_RATE_ORDER_2 = 2


class TestPokemonGrowthRateRepositorySave:
    """Test scope for save method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_growth_rate_repository_save_success(pokemon_growth_rate_repository):
        """Should persist pokemon growth rate when data is valid"""
        repository = pokemon_growth_rate_repository
        pokemon_growth_rate = await repository.save(
            entity=PokemonGrowthRate(
                url='https://pokeapi.co/api/v2/growth-rate/1/',
                name='slow',
                order=MOCK_GROWTH_RATE_ORDER,
                formula='\\frac{5x^3}{4}',
                description='',
            )
        )

        assert pokemon_growth_rate.url == 'https://pokeapi.co/api/v2/growth-rate/1/'
        assert pokemon_growth_rate.name == 'slow'
        assert pokemon_growth_rate.order == MOCK_GROWTH_RATE_ORDER
        assert pokemon_growth_rate.formula == '\\frac{5x^3}{4}'

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_growth_rate_repository_save_with_complex_formula(
        pokemon_growth_rate_repository,
    ):
        """Should persist pokemon growth rate with complex formula when valid"""
        repository = pokemon_growth_rate_repository
        pokemon_growth_rate = await repository.save(
            entity=(
                PokemonGrowthRate(
                    url='https://pokeapi.co/api/v2/growth-rate/2/',
                    name='medium',
                    order=MOCK_GROWTH_RATE_ORDER_2,
                    formula='x^3',
                    description='',
                )
            )
        )

        assert pokemon_growth_rate.url == 'https://pokeapi.co/api/v2/growth-rate/2/'
        assert pokemon_growth_rate.name == 'medium'
        assert pokemon_growth_rate.order == MOCK_GROWTH_RATE_ORDER_2
        assert pokemon_growth_rate.formula == 'x^3'

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_growth_rate_repository_save_commit_error(
        session, pokemon_growth_rate_repository
    ):
        """Should raise exception when database commit fails"""
        session.commit = AsyncMock(side_effect=Exception('Database error'))

        repository = pokemon_growth_rate_repository

        with pytest.raises(Exception, match='Database error'):
            await repository.save(
                entity=PokemonGrowthRate(
                    url='https://pokeapi.co/api/v2/growth-rate/1/',
                    name='slow',
                    order=MOCK_GROWTH_RATE_ORDER,
                    formula='\\frac{5x^3}{4}',
                    description='',
                )
            )


class TestPokemonGrowthRateRepositoryFindBy:
    """Test scope for find by method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_growth_rate_repository_find_by_not_found(
        pokemon_growth_rate_repository,
    ):
        """Should return None when pokemon growth rate is not found"""
        repository = pokemon_growth_rate_repository
        result = await repository.find_by(order=999)

        assert result is None

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_growth_rate_repository_find_by_order_success(
        pokemon_growth_rate, pokemon_growth_rate_repository
    ):
        """Should return pokemon growth rate when found by order"""
        repository = pokemon_growth_rate_repository
        result = await repository.find_by(order=MOCK_GROWTH_RATE_ORDER)

        assert result is not None
        assert isinstance(result, PokemonGrowthRate)
        assert result.order == MOCK_GROWTH_RATE_ORDER
        assert result.name == 'slow'
        assert result.formula == pokemon_growth_rate.formula

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_growth_rate_repository_find_by_order_medium(
        session, pokemon_growth_rate_repository
    ):
        """Should return medium growth rate when found by order"""
        pokemon_growth_rate = PokemonGrowthRate(
            url='https://pokeapi.co/api/v2/growth-rate/2/',
            name='medium',
            order=MOCK_GROWTH_RATE_ORDER_2,
            formula='x^3',
            description='Medium growth rate formula',
        )
        session.add(pokemon_growth_rate)
        await session.commit()

        repository = pokemon_growth_rate_repository
        result = await repository.find_by(order=MOCK_GROWTH_RATE_ORDER_2)

        assert result is not None
        assert isinstance(result, PokemonGrowthRate)
        assert result.order == MOCK_GROWTH_RATE_ORDER_2
        assert result.name == 'medium'
        assert result.formula == 'x^3'
