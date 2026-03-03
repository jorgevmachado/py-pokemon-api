from http import HTTPStatus
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from app.domain.captured_pokemon.schema import CapturedPokemonFilterPage

MOCK_EXP_GAINED = 10
MOCK_EV_AMOUNT = 10
MOCK_EV_CAP = 252


class TestCapturedPokemonServiceCreate:
    """Test scope for create method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_create_returns_captured_pokemon(captured_pokemon_service, trainer, pokemon):
        """Should create captured pokemon for trainer"""

        result = await captured_pokemon_service.create(pokemon=pokemon, trainer=trainer)

        assert result.pokemon_id == pokemon.id
        assert result.trainer_id == trainer.id
        assert result.nickname is not None


class TestCapturedPokemonServiceRecordBattleWin:
    """Test scope for record_battle_win method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_record_battle_win_increments_stats(
        captured_pokemon_service, trainer, pokemon
    ):
        """Should increment wins and battles"""
        captured_pokemon = await captured_pokemon_service.create(
            pokemon=pokemon, trainer=trainer
        )
        wins_before = captured_pokemon.wins
        battles_before = captured_pokemon.battles

        result = await captured_pokemon_service.record_battle_win(
            captured_pokemon=captured_pokemon,
            exp_gained=MOCK_EXP_GAINED,
        )

        assert result.wins == wins_before + 1
        assert result.battles == battles_before + 1
        assert result.experience >= MOCK_EXP_GAINED


class TestCapturedPokemonServiceRecordBattleLoss:
    """Test scope for record_battle_loss method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_record_battle_loss_increments_stats(
        captured_pokemon_service, trainer, pokemon
    ):
        """Should increment losses and battles"""
        captured_pokemon = await captured_pokemon_service.create(
            pokemon=pokemon, trainer=trainer
        )
        losses_before = captured_pokemon.losses
        battles_before = captured_pokemon.battles

        result = await captured_pokemon_service.record_battle_loss(
            captured_pokemon=captured_pokemon
        )

        assert result.losses == losses_before + 1
        assert result.battles == battles_before + 1


class TestCapturedPokemonServiceAddEffortValue:
    """Test scope for add_effort_value method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_add_effort_value_increases_ev(captured_pokemon_service, trainer, pokemon):
        """Should increase EV value"""
        captured_pokemon = await captured_pokemon_service.create(
            pokemon=pokemon, trainer=trainer
        )
        ev_before = captured_pokemon.ev_hp

        result = await captured_pokemon_service.add_effort_value(
            captured_pokemon=captured_pokemon,
            ev_type='hp',
            ev_amount=MOCK_EV_AMOUNT,
        )

        assert result.ev_hp == ev_before + MOCK_EV_AMOUNT

    @staticmethod
    @pytest.mark.asyncio
    async def test_add_effort_value_caps_ev(captured_pokemon_service, trainer, pokemon):
        """Should cap EV at 252"""
        captured_pokemon = await captured_pokemon_service.create(
            pokemon=pokemon, trainer=trainer
        )
        captured_pokemon.ev_hp = MOCK_EV_CAP

        result = await captured_pokemon_service.add_effort_value(
            captured_pokemon=captured_pokemon,
            ev_type='hp',
            ev_amount=MOCK_EV_AMOUNT,
        )

        assert result.ev_hp == MOCK_EV_CAP


class TestCapturedPokemonServiceRecalculateStats:
    """Test scope for recalculate_stats_for_level_up method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_recalculate_stats_updates_values(
        captured_pokemon_service, trainer, pokemon
    ):
        """Should update calculated stats"""
        captured_pokemon = await captured_pokemon_service.create(
            pokemon=pokemon, trainer=trainer
        )

        # Ensure required base stats are defined
        pokemon.hp = pokemon.hp or 1
        pokemon.attack = pokemon.attack or 1
        pokemon.defense = pokemon.defense or 1
        pokemon.special_attack = pokemon.special_attack or 1
        pokemon.special_defense = pokemon.special_defense or 1
        pokemon.speed = pokemon.speed or 1
        captured_pokemon.iv_hp = captured_pokemon.iv_hp or 0
        captured_pokemon.ev_hp = captured_pokemon.ev_hp or 0
        captured_pokemon.iv_attack = captured_pokemon.iv_attack or 0
        captured_pokemon.ev_attack = captured_pokemon.ev_attack or 0
        captured_pokemon.iv_defense = captured_pokemon.iv_defense or 0
        captured_pokemon.ev_defense = captured_pokemon.ev_defense or 0
        captured_pokemon.iv_special_attack = captured_pokemon.iv_special_attack or 0
        captured_pokemon.ev_special_attack = captured_pokemon.ev_special_attack or 0
        captured_pokemon.iv_special_defense = captured_pokemon.iv_special_defense or 0
        captured_pokemon.ev_special_defense = captured_pokemon.ev_special_defense or 0
        captured_pokemon.iv_speed = captured_pokemon.iv_speed or 0
        captured_pokemon.ev_speed = captured_pokemon.ev_speed or 0

        result = await captured_pokemon_service.recalculate_stats_for_level_up(
            captured_pokemon=captured_pokemon,
            pokemon=pokemon,
        )

        assert result.hp >= 1
        assert result.max_hp == result.hp
        assert result.attack >= 1
        assert result.defense >= 1
        assert result.special_attack >= 1
        assert result.special_defense >= 1
        assert result.speed >= 1


class TestCapturedPokemonServiceFetchAll:
    """Test scope for fetch_all method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_fetch_all_returns_entries(captured_pokemon_service, trainer):
        """Should return captured pokemon entries when repository succeeds"""
        expected_result = ['entry_1', 'entry_2']
        page_filter = CapturedPokemonFilterPage(trainer_id=trainer.id)
        captured_pokemon_service.repository.list_all = AsyncMock(return_value=expected_result)

        result = await captured_pokemon_service.fetch_all(page_filter=page_filter)

        assert result == expected_result
        captured_pokemon_service.repository.list_all.assert_awaited_once_with(
            page_filter=page_filter
        )

    @staticmethod
    @pytest.mark.asyncio
    async def test_fetch_all_raises_http_exception_on_repository_error(
        captured_pokemon_service,
        trainer,
    ):
        """Should raise HTTPException when repository fails"""
        page_filter = CapturedPokemonFilterPage(trainer_id=trainer.id)
        captured_pokemon_service.repository.list_all = AsyncMock(side_effect=Exception('boom'))

        with pytest.raises(HTTPException) as exc_info:
            await captured_pokemon_service.fetch_all(page_filter=page_filter)

        assert exc_info.value.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert exc_info.value.detail == 'Error fetching captured_pokemons entries'


class TestCapturedPokemonServiceFindByPokemon:
    """Test scope for find_by_pokemon method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_find_by_pokemon_returns_entry(
        captured_pokemon_service,
        trainer,
        pokemon,
    ):
        """Should return captured pokemon when repository finds a match"""
        expected_result = {'pokemon_id': pokemon.id, 'trainer_id': trainer.id}
        captured_pokemon_service.repository.find_by_pokemon = AsyncMock(
            return_value=expected_result
        )

        result = await captured_pokemon_service.find_by_pokemon(
            trainer_id=trainer.id,
            pokemon_id=pokemon.id,
        )

        assert result == expected_result
        captured_pokemon_service.repository.find_by_pokemon.assert_awaited_once_with(
            trainer_id=trainer.id,
            pokemon_id=pokemon.id,
        )

    @staticmethod
    @pytest.mark.asyncio
    async def test_find_by_pokemon_raises_http_exception_on_repository_error(
        captured_pokemon_service,
        trainer,
        pokemon,
    ):
        """Should raise HTTPException when repository fails"""
        captured_pokemon_service.repository.find_by_pokemon = AsyncMock(
            side_effect=Exception('boom')
        )

        with pytest.raises(HTTPException) as exc_info:
            await captured_pokemon_service.find_by_pokemon(
                trainer_id=trainer.id,
                pokemon_id=pokemon.id,
            )

        assert exc_info.value.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert exc_info.value.detail == 'Error find by pokemon'
