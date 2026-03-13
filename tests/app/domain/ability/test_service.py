from unittest.mock import AsyncMock

import pytest

from app.domain.ability.model import PokemonAbility
from app.domain.pokemon.external.schemas import (
    PokemonExternalBase,
    PokemonExternalBaseAbilitySchemaResponse,
)

MOCK_POKEMON_ABILITY_SLOT = 1
MOCK_POKEMON_ABILITY_SLOT_2 = 2
MOCK_POKEMON_ABILITY_IS_HIDDEN = False
TOTAL_ABILITIES_MULTIPLE = 2


class TestPokemonAbilityServiceVerifyPokemonAbilities:
    """Test scope for verify_pokemon_abilities method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_verify_pokemon_abilities_in_database_success(pokemon_ability_service):
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
        repository = pokemon_ability_service.repository
        repository.find_by = AsyncMock(return_value=pokemon_ability)

        result = await pokemon_ability_service.verify_pokemon_abilities(
            abilities=[response_pokemon_ability]
        )

        assert len(result) == total_results
        assert result[0].name == 'stench'
        assert result[0].order == 1
        assert result[0].slot == MOCK_POKEMON_ABILITY_SLOT
        assert result[0].is_hidden is MOCK_POKEMON_ABILITY_IS_HIDDEN
        repository.find_by.assert_called_once()

    @staticmethod
    @pytest.mark.asyncio
    async def test_verify_pokemon_abilities_not_in_database_success(pokemon_ability_service):
        """Should create and return pokemon ability when it does not exist in database"""
        total_results = 1
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
        repository = pokemon_ability_service.repository
        repository.find_by = AsyncMock(return_value=None)
        repository.save = AsyncMock(return_value=pokemon_ability)

        result = await pokemon_ability_service.verify_pokemon_abilities(
            abilities=[response_pokemon_ability]
        )

        assert len(result) == total_results
        assert result[0].name == 'stench'
        assert result[0].order == pokemon_ability_order
        assert result[0].slot == MOCK_POKEMON_ABILITY_SLOT
        assert result[0].is_hidden is MOCK_POKEMON_ABILITY_IS_HIDDEN
        repository.find_by.assert_called_once()
        repository.save.assert_called_once()

    @staticmethod
    @pytest.mark.asyncio
    async def test_verify_pokemon_abilities_with_hidden_ability(pokemon_ability_service):
        """Should create and return hidden pokemon ability when not in database"""
        total_results = 1
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
        repository = pokemon_ability_service.repository
        repository.find_by = AsyncMock(return_value=None)
        repository.save = AsyncMock(return_value=pokemon_ability)

        result = await pokemon_ability_service.verify_pokemon_abilities(
            abilities=[response_pokemon_ability]
        )

        assert len(result) == total_results
        assert result[0].name == 'static'
        assert result[0].order == pokemon_ability_order
        assert result[0].slot == MOCK_POKEMON_ABILITY_SLOT_2
        assert result[0].is_hidden is True
        repository.find_by.assert_called_once()
        repository.save.assert_called_once()

    @staticmethod
    @pytest.mark.asyncio
    async def test_verify_pokemon_abilities_empty_list(pokemon_ability_service):
        """Should return empty list when abilities list is empty"""
        repository = pokemon_ability_service.repository
        repository.find_by = AsyncMock()

        result = await pokemon_ability_service.verify_pokemon_abilities(abilities=[])

        assert len(result) == 0
        repository.find_by.assert_not_called()

    @staticmethod
    @pytest.mark.asyncio
    async def test_verify_pokemon_abilities_multiple_abilities(pokemon_ability_service):
        """Should process multiple abilities correctly"""
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
        repository = pokemon_ability_service.repository
        repository.find_by = AsyncMock(side_effect=[pokemon_ability_1, pokemon_ability_2])

        result = await pokemon_ability_service.verify_pokemon_abilities(
            abilities=response_abilities
        )

        assert len(result) == TOTAL_ABILITIES_MULTIPLE
        assert result[0].name == 'stench'
        assert result[0].is_hidden is MOCK_POKEMON_ABILITY_IS_HIDDEN
        assert result[1].name == 'static'
        assert result[1].is_hidden is True
        assert repository.find_by.call_count == TOTAL_ABILITIES_MULTIPLE

    @staticmethod
    @pytest.mark.asyncio
    async def test_verify_pokemon_abilities_mixed_database_and_new(pokemon_ability_service):
        """Should return abilities from database and create new ones"""
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
        repository = pokemon_ability_service.repository
        repository.find_by = AsyncMock(side_effect=[pokemon_ability_1, None])
        repository.save = AsyncMock(return_value=pokemon_ability_2)

        result = await pokemon_ability_service.verify_pokemon_abilities(
            abilities=response_abilities
        )

        assert len(result) == TOTAL_ABILITIES_MULTIPLE
        assert result[0].name == 'stench'
        assert result[1].name == 'static'
        assert repository.find_by.call_count == TOTAL_ABILITIES_MULTIPLE
        repository.save.assert_called_once()

    @staticmethod
    @pytest.mark.asyncio
    async def test_verify_pokemon_abilities_error(pokemon_ability_service):
        """Should return pokemon ability error when repository error occurs"""
        response_pokemon_ability = PokemonExternalBaseAbilitySchemaResponse(
            ability=PokemonExternalBase(
                name='stench', url='https://pokeapi.co/api/v2/ability/1/'
            ),
            slot=MOCK_POKEMON_ABILITY_SLOT,
            is_hidden=MOCK_POKEMON_ABILITY_IS_HIDDEN,
        )
        repository = pokemon_ability_service.repository
        repository.find_by = AsyncMock(side_effect=Exception('Database error'))

        result = await pokemon_ability_service.verify_pokemon_abilities(
            abilities=[response_pokemon_ability]
        )

        assert len(result) == 0
        repository.find_by.assert_called_once()
