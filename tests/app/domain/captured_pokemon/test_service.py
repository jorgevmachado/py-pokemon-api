from http import HTTPStatus
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from app.domain.captured_pokemon.schema import (
    CapturePokemonHealSchema,
    CapturePokemonSchema,
    PartialCapturedPokemonSchema,
)
from app.shared.schemas import FilterPage

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

    @staticmethod
    @pytest.mark.asyncio
    async def test_create_assigns_moves_from_pokemon(
        captured_pokemon_service, trainer, pokemon
    ):
        total_moves = 4
        """Should assign moves from pokemon to captured pokemon"""
        result = await captured_pokemon_service.create(pokemon=pokemon, trainer=trainer)

        # Pokemon should have moves assigned to captured_pokemon
        assert result.moves is not None
        # If pokemon has moves, they should be assigned (respecting max 4)
        if pokemon.moves:
            assert len(result.moves) <= total_moves
            for move in result.moves:
                assert move in pokemon.moves


class TestCapturedPokemonServiceFetchAll:
    """Test scope for fetch_all method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_fetch_all_returns_entries(captured_pokemon_service, trainer):
        """Should return captured pokemon entries when repository succeeds"""
        expected_result = ['entry_1', 'entry_2']
        captured_pokemon_service.repository.list_all = AsyncMock(return_value=expected_result)

        result = await captured_pokemon_service.fetch_all(trainer_id=trainer.id)

        assert result == expected_result
        captured_pokemon_service.repository.list_all.assert_awaited_once()
        call_args = captured_pokemon_service.repository.list_all.await_args.kwargs
        page_filter = call_args['page_filter']

        assert page_filter.model_dump(exclude_none=True) == {
            'trainer_id': trainer.id,
        }

    @staticmethod
    @pytest.mark.asyncio
    async def test_fetch_all_returns_entries_with_page_filter(
        captured_pokemon_service,
        trainer,
    ):
        """Should pass page filter to repository when provided"""
        expected_result = ['entry_1']
        page_filter = FilterPage.build(limit=10, offset=0, trainer_id=trainer.id)
        captured_pokemon_service.repository.list_all = AsyncMock(return_value=expected_result)

        result = await captured_pokemon_service.fetch_all(
            trainer_id=trainer.id, page_filter=page_filter
        )

        assert result == expected_result
        captured_pokemon_service.repository.list_all.assert_awaited_once()
        call_args = captured_pokemon_service.repository.list_all.await_args.kwargs
        page_filter = call_args['page_filter']

        assert page_filter.model_dump(exclude_none=True) == {
            'offset': 0,
            'limit': 10,
            'trainer_id': trainer.id,
        }

    @staticmethod
    @pytest.mark.asyncio
    async def test_fetch_all_raises_http_exception_on_repository_error(
        captured_pokemon_service,
        trainer,
    ):
        """Should raise HTTPException when repository fails"""
        captured_pokemon_service.repository.list_all = AsyncMock(side_effect=Exception('boom'))

        with pytest.raises(HTTPException) as exc_info:
            await captured_pokemon_service.fetch_all(trainer_id=trainer.id)

        assert exc_info.value.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert exc_info.value.detail == 'Internal server error'


class TestCapturedPokemonServiceCapture:
    """Test scope for capture method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_capture_creates_entry_when_requirements_are_met(
        captured_pokemon_service,
        trainer,
        pokemon,
    ):
        """Should create captured pokemon when trainer can capture"""

        trainer.pokeballs = 5
        trainer.capture_rate = 100
        pokemon.capture_rate = 30
        captured_pokemon_service.pokemon_service.fetch_one = AsyncMock(return_value=pokemon)

        expected_result = {'pokemon_id': pokemon.id, 'trainer_id': trainer.id}
        captured_pokemon_service.repository.find_by = AsyncMock(return_value=None)
        captured_pokemon_service.create = AsyncMock(return_value=expected_result)

        result = await captured_pokemon_service.capture(
            trainer=trainer,
            capture_pokemon=CapturePokemonSchema(pokemon_name=pokemon.name),
        )

        assert result == expected_result
        captured_pokemon_service.repository.find_by.assert_awaited_once()
        captured_pokemon_service.create.assert_awaited_once_with(
            pokemon=pokemon,
            trainer=trainer,
            nickname=pokemon.name,
        )

    @staticmethod
    @pytest.mark.asyncio
    async def test_capture_uses_suffix_when_nickname_already_exists(
        captured_pokemon_service,
        trainer,
        pokemon,
    ):
        """Should append suffix when nickname already exists for captured pokemon"""
        trainer.pokeballs = 5
        trainer.capture_rate = 100
        pokemon.capture_rate = 30
        captured_pokemon_service.pokemon_service.fetch_one = AsyncMock(return_value=pokemon)

        existing_pokemon = type('ExistingPokemon', (), {'nickname': 'sparky'})()
        captured_pokemon_service.repository.find_by = AsyncMock(return_value=existing_pokemon)
        captured_pokemon_service.create = AsyncMock(return_value={'ok': True})

        await captured_pokemon_service.capture(
            trainer=trainer,
            capture_pokemon=CapturePokemonSchema(
                pokemon_name=pokemon.name,
                nickname='sparky',
            ),
        )

        captured_pokemon_service.create.assert_awaited_once_with(
            pokemon=pokemon,
            trainer=trainer,
            nickname=f'{pokemon.name}_1',
        )

    @staticmethod
    @pytest.mark.asyncio
    async def test_capture_raises_forbidden_when_trainer_has_no_pokeballs(
        captured_pokemon_service,
        trainer,
        pokemon,
    ):
        """Should raise forbidden when trainer has no pokeballs"""
        trainer.pokeballs = 0
        captured_pokemon_service.pokemon_service.fetch_one = AsyncMock(return_value=pokemon)

        with pytest.raises(HTTPException) as exc_info:
            await captured_pokemon_service.capture(
                trainer=trainer,
                capture_pokemon=CapturePokemonSchema(pokemon_name=pokemon.name),
            )

        assert exc_info.value.status_code == HTTPStatus.FORBIDDEN
        assert exc_info.value.detail == 'Not enough pokeballs'

    @staticmethod
    @pytest.mark.asyncio
    async def test_capture_raises_forbidden_when_capture_rate_is_low(
        captured_pokemon_service,
        trainer,
        pokemon,
    ):
        """Should raise forbidden when trainer capture rate is below pokemon requirement"""
        trainer.pokeballs = 5
        trainer.capture_rate = 45
        pokemon.capture_rate = 65
        captured_pokemon_service.pokemon_service.fetch_one = AsyncMock(return_value=pokemon)

        with pytest.raises(HTTPException) as exc_info:
            await captured_pokemon_service.capture(
                trainer=trainer,
                capture_pokemon=CapturePokemonSchema(pokemon_name=pokemon.name),
            )

        assert exc_info.value.status_code == HTTPStatus.FORBIDDEN
        assert (
            exc_info.value.detail
            == 'You have 45 capture rate. To capture this Pokemon, you need 65.'
        )

    @staticmethod
    @pytest.mark.asyncio
    async def test_capture_raises_internal_server_error_on_unexpected_exception(
        captured_pokemon_service,
        trainer,
        pokemon,
    ):
        """Should raise internal server error when unexpected exception occurs"""
        trainer.pokeballs = 5
        trainer.capture_rate = 100
        pokemon.capture_rate = 30
        captured_pokemon_service.pokemon_service.fetch_one = AsyncMock(return_value=pokemon)
        captured_pokemon_service.repository.find_by = AsyncMock(side_effect=Exception('boom'))

        with pytest.raises(HTTPException) as exc_info:
            await captured_pokemon_service.capture(
                trainer=trainer,
                capture_pokemon=CapturePokemonSchema(pokemon_name=pokemon.name),
            )

        assert exc_info.value.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert exc_info.value.detail == 'Internal server error'


class TestCapturedPokemonServiceUpdate:
    """Test scope for update method"""

    EXPECTED_LEVEL = 2
    EXPECTED_WINS = 1
    EXPECTED_LOSSES = 1
    EXPECTED_HP = 15
    EXPECTED_SPEED = 6
    EXPECTED_ATTACK = 7
    EXPECTED_DEFENSE = 8
    EXPECTED_SPECIAL_ATTACK = 9
    EXPECTED_SPECIAL_DEFENSE = 10
    EXPECTED_EXPERIENCE = 25

    @staticmethod
    @pytest.mark.asyncio
    async def test_update_raises_not_found_when_missing(captured_pokemon_service):
        """Should raise not found when captured pokemon does not exist"""
        captured_pokemon_service.repository.find_by = AsyncMock(return_value=None)

        with pytest.raises(HTTPException) as exc_info:
            await captured_pokemon_service.update(
                param='missing-id',
                update_schema=PartialCapturedPokemonSchema(hp=10),
            )

        assert exc_info.value.status_code == HTTPStatus.NOT_FOUND
        assert exc_info.value.detail == 'Captured Pokemon not found'

    @staticmethod
    @pytest.mark.asyncio
    async def test_update_applies_partial_fields(captured_pokemon_service):
        """Should update only informed fields and persist"""
        captured = type(
            'Captured',
            (),
            {
                'level': 1,
                'wins': 0,
                'losses': 0,
                'hp': 10,
                'speed': 5,
                'attack': 6,
                'defense': 7,
                'special_attack': 8,
                'special_defense': 9,
                'experience': 0,
            },
        )()

        captured_pokemon_service.repository.find_by = AsyncMock(return_value=captured)
        captured_pokemon_service.repository.update = AsyncMock(return_value=captured)

        update_schema = PartialCapturedPokemonSchema(
            level=TestCapturedPokemonServiceUpdate.EXPECTED_LEVEL,
            wins=TestCapturedPokemonServiceUpdate.EXPECTED_WINS,
            losses=TestCapturedPokemonServiceUpdate.EXPECTED_LOSSES,
            hp=TestCapturedPokemonServiceUpdate.EXPECTED_HP,
            speed=TestCapturedPokemonServiceUpdate.EXPECTED_SPEED,
            attack=TestCapturedPokemonServiceUpdate.EXPECTED_ATTACK,
            defense=TestCapturedPokemonServiceUpdate.EXPECTED_DEFENSE,
            special_attack=TestCapturedPokemonServiceUpdate.EXPECTED_SPECIAL_ATTACK,
            special_defense=TestCapturedPokemonServiceUpdate.EXPECTED_SPECIAL_DEFENSE,
            experience=TestCapturedPokemonServiceUpdate.EXPECTED_EXPERIENCE,
        )

        result = await captured_pokemon_service.update(
            param='captured-id',
            update_schema=update_schema,
        )

        assert result.level == TestCapturedPokemonServiceUpdate.EXPECTED_LEVEL
        assert result.wins == TestCapturedPokemonServiceUpdate.EXPECTED_WINS
        assert result.losses == TestCapturedPokemonServiceUpdate.EXPECTED_LOSSES
        assert result.hp == TestCapturedPokemonServiceUpdate.EXPECTED_HP
        assert result.speed == TestCapturedPokemonServiceUpdate.EXPECTED_SPEED
        assert result.attack == TestCapturedPokemonServiceUpdate.EXPECTED_ATTACK
        assert result.defense == TestCapturedPokemonServiceUpdate.EXPECTED_DEFENSE
        assert (
            result.special_attack == TestCapturedPokemonServiceUpdate.EXPECTED_SPECIAL_ATTACK
        )
        assert (
            result.special_defense == TestCapturedPokemonServiceUpdate.EXPECTED_SPECIAL_DEFENSE
        )
        assert result.experience == TestCapturedPokemonServiceUpdate.EXPECTED_EXPERIENCE
        captured_pokemon_service.repository.update.assert_awaited_once()


class TestCapturedPokemonServiceHeal:
    """Test scope for heal method"""

    POKEMON_A_INITIAL_HP = 10
    POKEMON_A_MAX_HP = 30
    POKEMON_B_INITIAL_HP = 5
    POKEMON_B_MAX_HP = 20
    EXPECTED_POKEMON_COUNT = 2
    EXPECTED_UPDATE_COUNT = 2
    POKEMON_OWN_INITIAL_HP = 1
    POKEMON_OWN_MAX_HP = 40

    @staticmethod
    @pytest.mark.asyncio
    async def test_heal_all_heals_every_pokemon(captured_pokemon_service, trainer):
        """Should heal all trainer pokemons when all=true"""
        pokemon_a = type(
            'P',
            (),
            {
                'hp': TestCapturedPokemonServiceHeal.POKEMON_A_INITIAL_HP,
                'max_hp': TestCapturedPokemonServiceHeal.POKEMON_A_MAX_HP,
            },
        )()
        pokemon_b = type(
            'P',
            (),
            {
                'hp': TestCapturedPokemonServiceHeal.POKEMON_B_INITIAL_HP,
                'max_hp': TestCapturedPokemonServiceHeal.POKEMON_B_MAX_HP,
            },
        )()

        captured_pokemon_service.repository.list_all = AsyncMock(
            return_value=[pokemon_a, pokemon_b]
        )
        captured_pokemon_service.repository.update = AsyncMock()

        result = await captured_pokemon_service.heal(
            trainer_id=trainer.id,
            heal_pokemons=CapturePokemonHealSchema(all=True, pokemons=[]),
        )

        assert len(result) == TestCapturedPokemonServiceHeal.EXPECTED_POKEMON_COUNT
        assert pokemon_a.hp == TestCapturedPokemonServiceHeal.POKEMON_A_MAX_HP
        assert pokemon_b.hp == TestCapturedPokemonServiceHeal.POKEMON_B_MAX_HP
        assert (
            captured_pokemon_service.repository.update.await_count
            == TestCapturedPokemonServiceHeal.EXPECTED_UPDATE_COUNT
        )

    @staticmethod
    @pytest.mark.asyncio
    async def test_heal_specific_filters_by_trainer(captured_pokemon_service, trainer):
        """Should heal only selected pokemons that belong to trainer"""
        own = type(
            'P',
            (),
            {
                'trainer_id': trainer.id,
                'hp': TestCapturedPokemonServiceHeal.POKEMON_OWN_INITIAL_HP,
                'max_hp': TestCapturedPokemonServiceHeal.POKEMON_OWN_MAX_HP,
            },
        )()
        other = type('P', (), {'trainer_id': 'other', 'hp': 2, 'max_hp': 50})()

        captured_pokemon_service.repository.find_by = AsyncMock(side_effect=[own, other])
        captured_pokemon_service.repository.update = AsyncMock()

        result = await captured_pokemon_service.heal(
            trainer_id=trainer.id,
            heal_pokemons=CapturePokemonHealSchema(all=False, pokemons=['a', 'b']),
        )

        assert result == [own]
        assert own.hp == TestCapturedPokemonServiceHeal.POKEMON_OWN_MAX_HP
        captured_pokemon_service.repository.update.assert_awaited_once_with(own)
