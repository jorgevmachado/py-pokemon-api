from http import HTTPStatus
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from app.domain.pokedex.schema import FindPokedexSchema, PokedexFilterPage
from tests.app.domain.pokedex.conftest import PokedexFactory

MOCK_STATS = {
    'hp': 10,
    'wins': 0,
    'level': 1,
    'iv_hp': 1,
    'ev_hp': 0,
    'losses': 0,
    'max_hp': 10,
    'battles': 0,
    'nickname': 'name',
    'iv_speed': 1,
    'ev_speed': 0,
    'iv_attack': 1,
    'ev_attack': 0,
    'iv_defense': 1,
    'ev_defense': 0,
    'experience': 1,
    'iv_special_attack': 1,
    'ev_special_attack': 0,
    'iv_special_defense': 1,
    'ev_special_defense': 0,
}


class DummyPokedex:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class DummyCapturedPokemon:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class TestPokedexServiceInitialize:
    """Test scope for initialize method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_initialize_creates_missing_entries(pokedex_service, trainer, pokemon):
        """Should create pokedex entries when missing"""
        result = await pokedex_service.initialize(
            trainer=trainer, pokemon=pokemon, pokemons=[pokemon]
        )

        assert len(result) == 1
        assert result[0].pokemon_id == pokemon.id
        assert result[0].trainer_id == trainer.id
        assert result[0].discovered is True

    @staticmethod
    @pytest.mark.asyncio
    async def test_initialize_skips_existing_entries(pokedex_service, trainer, pokemon):
        """Should skip pokedex entries that already exist"""
        await pokedex_service.initialize(trainer=trainer, pokemon=pokemon, pokemons=[pokemon])
        result = await pokedex_service.initialize(
            trainer=trainer, pokemon=pokemon, pokemons=[pokemon]
        )

        assert result == []

    @staticmethod
    @pytest.mark.asyncio
    async def test_initialize_marks_discovered_false_when_no_pokemon(
        pokedex_service, trainer, pokemon
    ):
        """Should mark discovered as false when pokemon is None"""
        result = await pokedex_service.initialize(
            trainer=trainer, pokemon=None, pokemons=[pokemon]
        )

        assert len(result) == 1
        assert result[0].discovered is False

    @staticmethod
    @pytest.mark.asyncio
    async def test_initialize_returns_empty_list_on_error(pokedex_service, trainer, pokemon):
        """Should return empty list when an exception occurs"""

        pokedex_service.repository.find_by_trainer = AsyncMock(side_effect=Exception('boom'))

        result = await pokedex_service.initialize(
            trainer=trainer, pokemon=pokemon, pokemons=[pokemon]
        )

        assert result == []


class TestPokedexServiceInitializeEntry:
    """Test scope for initialize_pokedex_entry method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_initialize_pokedex_entry_raises_type_error(
        pokedex_service, trainer, pokemon
    ):
        """Should raise TypeError with current model signature"""
        with pytest.raises(TypeError):
            await pokedex_service.initialize_pokedex_entry(pokemon=pokemon, trainer=trainer)

    @staticmethod
    @pytest.mark.asyncio
    async def test_initialize_pokedex_entry_persists(pokedex_service, trainer, pokemon):
        """Should add, commit, and refresh a pokedex entry"""
        pokedex_service.business.calculate_pokemon_stats = MagicMock(return_value=MOCK_STATS)
        pokedex_service.session = AsyncMock()

        with patch('app.domain.pokedex.service.Pokedex', DummyPokedex):
            result = await pokedex_service.initialize_pokedex_entry(
                pokemon=pokemon, trainer=trainer
            )

        assert result.pokemon_id == pokemon.id
        assert result.trainer_id == trainer.id
        pokedex_service.session.add.assert_called_once_with(result)
        pokedex_service.session.commit.assert_called_once()
        pokedex_service.session.refresh.assert_called_once_with(result)


class TestPokedexServiceCapturePokemon:
    """Test scope for capture_pokemon method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_capture_pokemon_raises_type_error(pokedex_service, trainer, pokemon):
        """Should raise TypeError with current model signature"""
        with pytest.raises(TypeError):
            await pokedex_service.capture_pokemon(pokemon=pokemon, trainer=trainer)

    @staticmethod
    @pytest.mark.asyncio
    async def test_capture_pokemon_persists(pokedex_service, trainer, pokemon):
        """Should add, commit, and refresh a captured pokemon"""
        pokedex_service.business.calculate_pokemon_stats = MagicMock(
            return_value={
                **MOCK_STATS,
                'attack': 1,
                'defense': 1,
                'special_attack': 1,
                'special_defense': 1,
                'speed': 1,
            }
        )
        pokedex_service.session = AsyncMock()

        with patch('app.domain.pokedex.service.CapturedPokemon', DummyCapturedPokemon):
            result = await pokedex_service.capture_pokemon(pokemon=pokemon, trainer=trainer)

        assert result.pokemon_id == pokemon.id
        assert result.trainer_id == trainer.id
        pokedex_service.session.add.assert_called_once_with(result)
        pokedex_service.session.commit.assert_called_once()
        pokedex_service.session.refresh.assert_called_once_with(result)


class TestPokedexServiceAddPokemonToPokedexAndCapture:
    """Test scope for add_pokemon_to_pokedex_and_capture method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_add_pokemon_to_pokedex_and_capture_returns_tuple(
        pokedex_service, trainer, pokemon
    ):
        """Should return pokedex and captured entries"""
        pokedex_entry = DummyPokedex(pokemon_id=pokemon.id, trainer_id=trainer.id)
        captured_entry = DummyCapturedPokemon(pokemon_id=pokemon.id, trainer_id=trainer.id)
        pokedex_service.initialize_pokedex_entry = AsyncMock(return_value=pokedex_entry)
        pokedex_service.capture_pokemon = AsyncMock(return_value=captured_entry)

        (
            result_pokedex,
            result_captured,
        ) = await pokedex_service.add_pokemon_to_pokedex_and_capture(
            pokemon=pokemon,
            trainer=trainer,
        )

        assert result_pokedex == pokedex_entry
        assert result_captured == captured_entry
        (
            pokedex_service.initialize_pokedex_entry.assert_called_once_with(
                pokemon=pokemon,
                trainer=trainer,
                level=1,
            )
        )
        (
            pokedex_service.capture_pokemon.assert_called_once_with(
                pokemon=pokemon,
                trainer=trainer,
                level=1,
            )
        )


class TestPokedexServiceFetchAll:
    """Test scope for fetch_all method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokedex_fetch_all_returns_list(
        session, pokedex_service, trainer, pokemon, pokemon_incomplete
    ):
        """Should return a list of pokedex entries"""
        pokedex_1 = PokedexFactory(trainer_id=trainer.id, pokemon_id=pokemon.id)
        session.add(pokedex_1)
        await session.commit()
        pokedex_2 = PokedexFactory(trainer_id=trainer.id, pokemon_id=pokemon_incomplete.id)
        session.add(pokedex_2)
        await session.commit()

        result = await pokedex_service.fetch_all(
            page_filter=PokedexFilterPage(trainer_id=trainer.id)
        )
        assert isinstance(result, list)
        assert len(result) >= 1

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokedex_fetch_all_returns_error(pokedex_service, trainer):
        """Should raise HTTPException when repository fails"""
        pokedex_service.repository.list_all = AsyncMock(side_effect=Exception('boom'))

        with pytest.raises(HTTPException) as exc_info:
            await pokedex_service.fetch_all(
                page_filter=PokedexFilterPage(trainer_id=trainer.id)
            )
        assert exc_info.value.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert exc_info.value.detail == 'Error fetching pokedex entries'


class TestPokedexServiceRefresh:
    """Test scope for refresh method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_refresh_creates_entries_for_missing_pokemon(
        pokedex_service, trainer, pokemon
    ):
        """Should create a new entry when pokemon is not present in pokedex"""
        pokedex_service.repository.find_by_pokemon = AsyncMock(return_value=None)
        pokedex_service.business.calculate_pokemon_stats = MagicMock(return_value=MOCK_STATS)
        pokedex_service.repository.create = AsyncMock(
            side_effect=lambda create_schema: DummyPokedex(**create_schema.model_dump())
        )

        result = await pokedex_service.refresh(
            trainer_id=trainer.id,
            pokemons=[pokemon],
        )

        assert len(result) == 1
        assert result[0].pokemon_id == pokemon.id
        assert result[0].trainer_id == trainer.id
        assert result[0].discovered is False
        pokedex_service.repository.find_by_pokemon.assert_awaited_once_with(
            FindPokedexSchema(
                trainer_id=trainer.id,
                pokemon_id=pokemon.id,
                name=None,
                nickname=None,
            )
        )
        pokedex_service.business.calculate_pokemon_stats.assert_called_once_with(
            pokemon=pokemon
        )
        pokedex_service.repository.create.assert_awaited_once()

    @staticmethod
    @pytest.mark.asyncio
    async def test_refresh_skips_existing_entries(
        pokedex_service,
        trainer,
        pokemon,
        pokemon_incomplete,
    ):
        """Should skip existing pokedex entries and create only missing ones"""
        pokedex_service.repository.find_by_pokemon = AsyncMock(
            side_effect=[DummyPokedex(pokemon_id=pokemon.id), None]
        )
        pokedex_service.business.calculate_pokemon_stats = MagicMock(return_value=MOCK_STATS)
        pokedex_service.repository.create = AsyncMock(
            side_effect=lambda create_schema: DummyPokedex(**create_schema.model_dump())
        )

        result = await pokedex_service.refresh(
            trainer_id=trainer.id,
            pokemons=[pokemon, pokemon_incomplete],
        )
        total_count = 2
        assert len(result) == 1
        assert result[0].pokemon_id == pokemon_incomplete.id
        assert result[0].trainer_id == trainer.id
        assert result[0].discovered is False
        assert pokedex_service.repository.find_by_pokemon.await_count == total_count
        pokedex_service.business.calculate_pokemon_stats.assert_called_once_with(
            pokemon=pokemon_incomplete
        )
        pokedex_service.repository.create.assert_awaited_once()

    @staticmethod
    @pytest.mark.asyncio
    async def test_refresh_returns_empty_list_for_empty_input(pokedex_service, trainer):
        """Should return an empty list when no pokemons are provided"""
        pokedex_service.repository.find_by_pokemon = AsyncMock()
        pokedex_service.repository.create = AsyncMock()
        pokedex_service.business.calculate_pokemon_stats = MagicMock()

        result = await pokedex_service.refresh(
            trainer_id=trainer.id,
            pokemons=[],
        )

        assert result == []
        pokedex_service.repository.find_by_pokemon.assert_not_awaited()
        pokedex_service.repository.create.assert_not_awaited()
        pokedex_service.business.calculate_pokemon_stats.assert_not_called()

    @staticmethod
    @pytest.mark.asyncio
    async def test_refresh_propagates_error_when_create_fails(
        pokedex_service,
        trainer,
        pokemon,
    ):
        """Should propagate exception when repository create fails"""
        pokedex_service.repository.find_by_pokemon = AsyncMock(return_value=None)
        pokedex_service.business.calculate_pokemon_stats = MagicMock(return_value=MOCK_STATS)
        pokedex_service.repository.create = AsyncMock(side_effect=Exception('boom'))

        with pytest.raises(Exception, match='boom'):
            await pokedex_service.refresh(
                trainer_id=trainer.id,
                pokemons=[pokemon],
            )


class TestPokedexServiceFindByPokemon:
    """Test scope for find_by_pokemon method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_find_by_pokemon_returns_entry(
        pokedex_service,
        trainer,
        pokemon,
    ):
        """Should return pokedex entry when found"""
        expected_result = {'pokemon_id': pokemon.id, 'trainer_id': trainer.id}
        pokedex_service.repository.find_by_pokemon = AsyncMock(return_value=expected_result)

        result = await pokedex_service.find_by_pokemon(
            find_pokedex=FindPokedexSchema(
                trainer_id=trainer.id,
                pokemon_id=pokemon.id,
            )
        )

        assert result == expected_result
        pokedex_service.repository.find_by_pokemon.assert_awaited_once()

    @staticmethod
    @pytest.mark.asyncio
    async def test_find_by_pokemon_returns_none_when_empty_params(
        pokedex_service,
        trainer,
    ):
        """Should return None when all parameters are empty"""

        result = await pokedex_service.find_by_pokemon(
            find_pokedex=FindPokedexSchema(
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
        pokedex_service,
        trainer,
        pokemon,
    ):
        """Should raise HTTPException when repository fails"""
        pokedex_service.repository.find_by_pokemon = AsyncMock(side_effect=Exception('boom'))

        with pytest.raises(HTTPException) as exc_info:
            await pokedex_service.find_by_pokemon(
                find_pokedex=FindPokedexSchema(
                    trainer_id=trainer.id,
                    pokemon_id=pokemon.id,
                )
            )

        assert exc_info.value.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert exc_info.value.detail == 'Error pokedex find by pokemon'
