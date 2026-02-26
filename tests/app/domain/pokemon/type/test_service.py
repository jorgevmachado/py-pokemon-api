from unittest.mock import AsyncMock, patch

import pytest

from app.domain.pokemon.external.schemas import (
    PokemonExternalBase,
    PokemonExternalBaseTypeSchemaResponse,
)
from app.domain.pokemon.type.business import PokemonTypeBusiness, TypeColor
from app.domain.pokemon.type.service import PokemonTypeService
from app.models import PokemonType


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

        type_color = TypeColor(
            id=3, name='fire', text_color='#fff', background_color='#fd7d24'
        )

        with patch.object(
            PokemonTypeBusiness,
            'ensure_colors',
            return_value=type_color,
        ):
            service.repository.find_one_by_order = AsyncMock(return_value=None)
            result = await service.verify_pokemon_type(types=[response_pokemon_type])

        assert len(result) == total_results
        assert result[0].name == 'fire'
        assert result[0].order == pokemon_type_order
        assert result[0].text_color == '#fff'
        assert result[0].background_color == '#fd7d24'
        service.repository.find_one_by_order.assert_called_once()

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
