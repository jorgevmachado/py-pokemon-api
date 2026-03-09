from unittest.mock import AsyncMock, patch

import pytest

from app.domain.growth_rate.business import PokemonGrowthRateBusiness
from app.domain.growth_rate.model import PokemonGrowthRate
from app.domain.pokemon.external.schemas import PokemonExternalBase
from app.domain.pokemon.external.schemas.growth_rate import (
    PokemonExternalGrowthRateSchemaResponse,
)

MOCK_GROWTH_RATE_ORDER = 1


class TestPokemonGrowthRateServiceVerifyPokemonGrowthRate:
    """Test scope for verify_pokemon_growth_rate method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_verify_pokemon_growth_rate_in_database_success(pokemon_growth_rate_service):
        """Should return pokemon growth rate from database when it exists"""
        pokemon_growth_rate = PokemonGrowthRate(
            url='https://pokeapi.co/api/v2/growth-rate/1/',
            name='slow',
            order=MOCK_GROWTH_RATE_ORDER,
            formula='\\frac{5x^3}{4}',
        )
        response_growth_rate = PokemonExternalBase(
            name='slow', url='https://pokeapi.co/api/v2/growth-rate/1/'
        )

        pokemon_growth_rate_service.repository.find_one_by_order = AsyncMock(
            return_value=pokemon_growth_rate
        )
        result = await pokemon_growth_rate_service.verify_pokemon_growth_rate(
            growth_rate=response_growth_rate
        )

        assert result is not None
        assert result.name == 'slow'
        assert result.order == MOCK_GROWTH_RATE_ORDER
        assert result.formula == '\\frac{5x^3}{4}'
        pokemon_growth_rate_service.repository.find_one_by_order.assert_called_once_with(
            order=MOCK_GROWTH_RATE_ORDER
        )

    @staticmethod
    @pytest.mark.asyncio
    async def test_verify_pokemon_growth_rate_not_in_database_success(
        pokemon_growth_rate_service,
    ):
        """Should create and return pokemon growth rate when not in database"""
        pokemon_growth_rate_order = MOCK_GROWTH_RATE_ORDER
        response_growth_rate = PokemonExternalBase(
            name='slow',
            url=f'https://pokeapi.co/api/v2/growth-rate/{pokemon_growth_rate_order}/',
        )

        external_growth_rate_data = PokemonExternalGrowthRateSchemaResponse(
            id=1,
            name='slow',
            formula='\\frac{5x^3}{4}',
            levels=[],
            descriptions=[],
        )

        pokemon_growth_rate = PokemonGrowthRate(
            url='https://pokeapi.co/api/v2/growth-rate/1/',
            name='slow',
            order=pokemon_growth_rate_order,
            formula='\\frac{5x^3}{4}',
        )

        pokemon_growth_rate_service.repository.find_one_by_order = AsyncMock(return_value=None)
        pokemon_growth_rate_service.repository.create = AsyncMock(
            return_value=pokemon_growth_rate
        )

        with patch.object(
            PokemonGrowthRateBusiness,
            'ensure_description_message',
            return_value='Slow growth rate description',
        ):
            with patch.object(
                pokemon_growth_rate_service.external_service,
                'pokemon_external_growth_rate_by_order',
                return_value=external_growth_rate_data,
            ):
                result = await pokemon_growth_rate_service.verify_pokemon_growth_rate(
                    growth_rate=response_growth_rate
                )

        assert result is not None
        assert result.name == 'slow'
        assert result.order == pokemon_growth_rate_order
        assert result.formula == '\\frac{5x^3}{4}'
        pokemon_growth_rate_service.repository.find_one_by_order.assert_called_once()
        pokemon_growth_rate_service.repository.create.assert_called_once()

    @staticmethod
    @pytest.mark.asyncio
    async def test_verify_pokemon_growth_rate_external_service_no_data(
        pokemon_growth_rate_service,
    ):
        """Should return None when external service returns no data"""
        response_growth_rate = PokemonExternalBase(
            name='unknown-growth-rate',
            url='https://pokeapi.co/api/v2/growth-rate/999/',
        )

        pokemon_growth_rate_service.repository.find_one_by_order = AsyncMock(return_value=None)

        with patch.object(
            pokemon_growth_rate_service.external_service,
            'pokemon_external_growth_rate_by_order',
            return_value=None,
        ):
            result = await pokemon_growth_rate_service.verify_pokemon_growth_rate(
                growth_rate=response_growth_rate
            )

        assert result is None
        pokemon_growth_rate_service.repository.find_one_by_order.assert_called_once()

    @staticmethod
    @pytest.mark.asyncio
    async def test_verify_pokemon_growth_rate_with_description(pokemon_growth_rate_service):
        """Should create growth rate with description from business logic"""
        response_growth_rate = PokemonExternalBase(
            name='medium',
            url='https://pokeapi.co/api/v2/growth-rate/2/',
        )

        external_growth_rate_data = PokemonExternalGrowthRateSchemaResponse(
            id=2,
            name='medium',
            formula='x^3',
            levels=[],
            descriptions=[],
        )

        pokemon_growth_rate = PokemonGrowthRate(
            url='https://pokeapi.co/api/v2/growth-rate/2/',
            name='medium',
            order=2,
            formula='x^3',
        )

        pokemon_growth_rate_service.repository.find_one_by_order = AsyncMock(return_value=None)
        pokemon_growth_rate_service.repository.create = AsyncMock(
            return_value=pokemon_growth_rate
        )

        expected_description = 'Medium growth rate description'

        with patch.object(
            PokemonGrowthRateBusiness,
            'ensure_description_message',
            return_value=expected_description,
        ) as mock_ensure_description:
            with patch.object(
                pokemon_growth_rate_service.external_service,
                'pokemon_external_growth_rate_by_order',
                return_value=external_growth_rate_data,
            ):
                result = await pokemon_growth_rate_service.verify_pokemon_growth_rate(
                    growth_rate=response_growth_rate
                )

        assert result is not None
        mock_ensure_description.assert_called_once_with(external_growth_rate_data.descriptions)
        pokemon_growth_rate_service.repository.create.assert_called_once()

    @staticmethod
    @pytest.mark.asyncio
    async def test_verify_pokemon_growth_rate_in_error(pokemon_growth_rate_service):
        """Should return pokemon growth rate error"""
        response_growth_rate = PokemonExternalBase(
            name='slow', url='https://pokeapi.co/api/v2/growth-rate/1/'
        )

        pokemon_growth_rate_service.repository.find_one_by_order = AsyncMock(
            side_effect=Exception('Database error')
        )
        result = await pokemon_growth_rate_service.verify_pokemon_growth_rate(
            growth_rate=response_growth_rate
        )

        assert not result
        pokemon_growth_rate_service.repository.find_one_by_order.assert_called_once()

    @staticmethod
    @pytest.mark.asyncio
    async def test_verify_pokemon_growth_rate_none(pokemon_growth_rate_service):
        """Should return pokemon growth rate error"""

        result = await pokemon_growth_rate_service.verify_pokemon_growth_rate(growth_rate=None)

        assert not result
