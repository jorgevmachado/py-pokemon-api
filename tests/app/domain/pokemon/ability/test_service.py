from unittest.mock import AsyncMock

import pytest

from app.domain.pokemon.ability.service import PokemonAbilityService
from app.domain.pokemon.external.schemas import (
    PokemonExternalBase,
    PokemonExternalBaseAbilitySchemaResponse,
)
from app.models import PokemonAbility

MOCK_POKEMON_ABILITY_SLOT = 1
MOCK_POKEMON_ABILITY_SLOT_2 = 2
MOCK_POKEMON_ABILITY_IS_HIDDEN = False
TOTAL_ABILITIES_MULTIPLE = 2


class TestPokemonAbilityServiceVerifyPokemonAbilities:
    """Test scope for verify_pokemon_abilities method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_verify_pokemon_abilities_in_database_success(session):
        """Should return pokemon ability from database when it exists"""
        total_results = 1
        pokemon_ability = PokemonAbility(
            url='https://pokeapi.co/api/v2/ability/1/',
            name='stench',
            order=1,
            slot=MOCK_POKEMON_ABILITY_SLOT,
            is_hidden=MOCK_POKEMON_ABILITY_IS_HIDDEN,
        )
        response_pokemon_ability = PokemonExternalBaseAbilitySchemaResponse(
            ability=PokemonExternalBase(
                name='stench', url='https://pokeapi.co/api/v2/ability/1/'
            ),
            slot=MOCK_POKEMON_ABILITY_SLOT,
            is_hidden=MOCK_POKEMON_ABILITY_IS_HIDDEN,
        )

        service = PokemonAbilityService(session=session)
        service.repository.find_one_by_order = AsyncMock(return_value=pokemon_ability)
        result = await service.verify_pokemon_abilities(abilities=[response_pokemon_ability])

        assert len(result) == total_results
        assert result[0].name == 'stench'
        assert result[0].order == 1
        assert result[0].slot == MOCK_POKEMON_ABILITY_SLOT
        assert result[0].is_hidden is MOCK_POKEMON_ABILITY_IS_HIDDEN
        service.repository.find_one_by_order.assert_called_once()

    @staticmethod
    @pytest.mark.asyncio
    async def test_verify_pokemon_abilities_not_in_database_success(session):
        """Should create and return pokemon ability when it does not exist in database"""
        total_results = 1
        service = PokemonAbilityService(session=session)
        pokemon_ability_order = 1
        response_pokemon_ability = PokemonExternalBaseAbilitySchemaResponse(
            ability=PokemonExternalBase(
                name='stench',
                url=f'https://pokeapi.co/api/v2/ability/{pokemon_ability_order}/',
            ),
            slot=MOCK_POKEMON_ABILITY_SLOT,
            is_hidden=MOCK_POKEMON_ABILITY_IS_HIDDEN,
        )

        pokemon_ability = PokemonAbility(
            url='https://pokeapi.co/api/v2/ability/1/',
            name='stench',
            order=pokemon_ability_order,
            slot=MOCK_POKEMON_ABILITY_SLOT,
            is_hidden=MOCK_POKEMON_ABILITY_IS_HIDDEN,
        )

        service.repository.find_one_by_order = AsyncMock(return_value=None)
        service.repository.create = AsyncMock(return_value=pokemon_ability)

        result = await service.verify_pokemon_abilities(abilities=[response_pokemon_ability])

        assert len(result) == total_results
        assert result[0].name == 'stench'
        assert result[0].order == pokemon_ability_order
        assert result[0].slot == MOCK_POKEMON_ABILITY_SLOT
        assert result[0].is_hidden is MOCK_POKEMON_ABILITY_IS_HIDDEN
        service.repository.find_one_by_order.assert_called_once()
        service.repository.create.assert_called_once()

    @staticmethod
    @pytest.mark.asyncio
    async def test_verify_pokemon_abilities_with_hidden_ability(session):
        """Should create and return hidden pokemon ability when not in database"""
        total_results = 1
        service = PokemonAbilityService(session=session)
        pokemon_ability_order = MOCK_POKEMON_ABILITY_SLOT_2
        response_pokemon_ability = PokemonExternalBaseAbilitySchemaResponse(
            ability=PokemonExternalBase(
                name='static',
                url=f'https://pokeapi.co/api/v2/ability/{pokemon_ability_order}/',
            ),
            slot=MOCK_POKEMON_ABILITY_SLOT_2,
            is_hidden=True,
        )

        pokemon_ability = PokemonAbility(
            url='https://pokeapi.co/api/v2/ability/2/',
            name='static',
            order=pokemon_ability_order,
            slot=MOCK_POKEMON_ABILITY_SLOT_2,
            is_hidden=True,
        )

        service.repository.find_one_by_order = AsyncMock(return_value=None)
        service.repository.create = AsyncMock(return_value=pokemon_ability)

        result = await service.verify_pokemon_abilities(abilities=[response_pokemon_ability])

        assert len(result) == total_results
        assert result[0].name == 'static'
        assert result[0].order == pokemon_ability_order
        assert result[0].slot == MOCK_POKEMON_ABILITY_SLOT_2
        assert result[0].is_hidden is True
        service.repository.find_one_by_order.assert_called_once()
        service.repository.create.assert_called_once()

    @staticmethod
    @pytest.mark.asyncio
    async def test_verify_pokemon_abilities_empty_list(session):
        """Should return empty list when abilities list is empty"""
        service = PokemonAbilityService(session=session)
        service.repository.find_one_by_order = AsyncMock()
        result = await service.verify_pokemon_abilities(abilities=[])

        assert len(result) == 0
        service.repository.find_one_by_order.assert_not_called()

    @staticmethod
    @pytest.mark.asyncio
    async def test_verify_pokemon_abilities_multiple_abilities(session):
        """Should process multiple abilities correctly"""
        service = PokemonAbilityService(session=session)

        pokemon_ability_1 = PokemonAbility(
            url='https://pokeapi.co/api/v2/ability/1/',
            name='stench',
            order=1,
            slot=MOCK_POKEMON_ABILITY_SLOT,
            is_hidden=MOCK_POKEMON_ABILITY_IS_HIDDEN,
        )

        pokemon_ability_2 = PokemonAbility(
            url='https://pokeapi.co/api/v2/ability/2/',
            name='static',
            order=MOCK_POKEMON_ABILITY_SLOT_2,
            slot=MOCK_POKEMON_ABILITY_SLOT_2,
            is_hidden=True,
        )

        response_abilities = [
            PokemonExternalBaseAbilitySchemaResponse(
                ability=PokemonExternalBase(
                    name='stench', url='https://pokeapi.co/api/v2/ability/1/'
                ),
                slot=MOCK_POKEMON_ABILITY_SLOT,
                is_hidden=MOCK_POKEMON_ABILITY_IS_HIDDEN,
            ),
            PokemonExternalBaseAbilitySchemaResponse(
                ability=PokemonExternalBase(
                    name='static', url='https://pokeapi.co/api/v2/ability/2/'
                ),
                slot=MOCK_POKEMON_ABILITY_SLOT_2,
                is_hidden=True,
            ),
        ]

        service.repository.find_one_by_order = AsyncMock(
            side_effect=[pokemon_ability_1, pokemon_ability_2]
        )

        result = await service.verify_pokemon_abilities(abilities=response_abilities)

        assert len(result) == TOTAL_ABILITIES_MULTIPLE
        assert result[0].name == 'stench'
        assert result[0].is_hidden is MOCK_POKEMON_ABILITY_IS_HIDDEN
        assert result[1].name == 'static'
        assert result[1].is_hidden is True
        assert service.repository.find_one_by_order.call_count == TOTAL_ABILITIES_MULTIPLE

    @staticmethod
    @pytest.mark.asyncio
    async def test_verify_pokemon_abilities_mixed_database_and_new(session):
        """Should return abilities from database and create new ones"""
        service = PokemonAbilityService(session=session)

        pokemon_ability_1 = PokemonAbility(
            url='https://pokeapi.co/api/v2/ability/1/',
            name='stench',
            order=1,
            slot=MOCK_POKEMON_ABILITY_SLOT,
            is_hidden=MOCK_POKEMON_ABILITY_IS_HIDDEN,
        )

        pokemon_ability_2 = PokemonAbility(
            url='https://pokeapi.co/api/v2/ability/2/',
            name='static',
            order=MOCK_POKEMON_ABILITY_SLOT_2,
            slot=MOCK_POKEMON_ABILITY_SLOT_2,
            is_hidden=True,
        )

        response_abilities = [
            PokemonExternalBaseAbilitySchemaResponse(
                ability=PokemonExternalBase(
                    name='stench', url='https://pokeapi.co/api/v2/ability/1/'
                ),
                slot=MOCK_POKEMON_ABILITY_SLOT,
                is_hidden=MOCK_POKEMON_ABILITY_IS_HIDDEN,
            ),
            PokemonExternalBaseAbilitySchemaResponse(
                ability=PokemonExternalBase(
                    name='static', url='https://pokeapi.co/api/v2/ability/2/'
                ),
                slot=MOCK_POKEMON_ABILITY_SLOT_2,
                is_hidden=True,
            ),
        ]

        service.repository.find_one_by_order = AsyncMock(side_effect=[pokemon_ability_1, None])
        service.repository.create = AsyncMock(return_value=pokemon_ability_2)

        result = await service.verify_pokemon_abilities(abilities=response_abilities)

        assert len(result) == TOTAL_ABILITIES_MULTIPLE
        assert result[0].name == 'stench'
        assert result[1].name == 'static'
        assert service.repository.find_one_by_order.call_count == TOTAL_ABILITIES_MULTIPLE
        service.repository.create.assert_called_once()
