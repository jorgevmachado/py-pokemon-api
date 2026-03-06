from http import HTTPStatus
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from app.domain.captured_pokemon.schema import (
    CapturedPokemonFilterPage,
    CapturePokemonSchema,
    FindCapturePokemonSchema,
)

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
        captured_pokemon_service.repository.list_all.assert_awaited_once_with(
            trainer_id=trainer.id, page_filter=None
        )

    @staticmethod
    @pytest.mark.asyncio
    async def test_fetch_all_returns_entries_with_page_filter(
        captured_pokemon_service,
        trainer,
    ):
        """Should pass page filter to repository when provided"""
        expected_result = ['entry_1']
        page_filter = CapturedPokemonFilterPage(limit=10, offset=0)
        captured_pokemon_service.repository.list_all = AsyncMock(return_value=expected_result)

        result = await captured_pokemon_service.fetch_all(
            trainer_id=trainer.id, page_filter=page_filter
        )

        assert result == expected_result
        captured_pokemon_service.repository.list_all.assert_awaited_once_with(
            trainer_id=trainer.id, page_filter=page_filter
        )

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
        """Should return captured pokemon when found"""

        # Create a captured pokemon first
        await captured_pokemon_service.create(
            pokemon=pokemon, trainer=trainer, nickname='test'
        )

        result = await captured_pokemon_service.find_by_pokemon(
            find_capture_pokemon=FindCapturePokemonSchema(
                trainer_id=trainer.id,
                pokemon_id=pokemon.id,
            )
        )

        assert result is not None
        assert result.pokemon_id == pokemon.id

    @staticmethod
    @pytest.mark.asyncio
    async def test_find_by_pokemon_returns_none_when_empty_params(
        captured_pokemon_service,
        trainer,
    ):
        """Should return None when all parameters are empty"""

        result = await captured_pokemon_service.find_by_pokemon(
            find_capture_pokemon=FindCapturePokemonSchema(
                trainer_id=trainer.id,
                pokemon_id=None,
                name=None,
                nickname=None,
            )
        )

        assert result is None

    @staticmethod
    @pytest.mark.asyncio
    async def test_find_by_pokemon_raises_http_exception_on_error(
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
                find_capture_pokemon=FindCapturePokemonSchema(
                    trainer_id=trainer.id,
                    pokemon_id=pokemon.id,
                )
            )

        assert exc_info.value.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert exc_info.value.detail == 'Error find by pokemon'


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
        captured_pokemon_service.find_by_pokemon = AsyncMock(return_value=None)
        captured_pokemon_service.create = AsyncMock(return_value=expected_result)

        result = await captured_pokemon_service.capture(
            trainer=trainer,
            capture_pokemon=CapturePokemonSchema(pokemon_name=pokemon.name),
        )

        assert result == expected_result
        captured_pokemon_service.find_by_pokemon.assert_awaited_once()
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
        captured_pokemon_service.find_by_pokemon = AsyncMock(return_value=existing_pokemon)
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
        captured_pokemon_service.find_by_pokemon = AsyncMock(side_effect=Exception('boom'))

        with pytest.raises(HTTPException) as exc_info:
            await captured_pokemon_service.capture(
                trainer=trainer,
                capture_pokemon=CapturePokemonSchema(pokemon_name=pokemon.name),
            )

        assert exc_info.value.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert exc_info.value.detail == 'Error capture pokemons'
