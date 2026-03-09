from http import HTTPStatus
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from app.domain.pokedex.schema import FindPokedexSchema
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

        result = await pokedex_service.fetch_all(trainer_id=trainer.id)
        assert isinstance(result, list)
        assert len(result) >= 1

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokedex_fetch_all_returns_error(pokedex_service, trainer):
        """Should raise HTTPException when repository fails"""
        pokedex_service.repository.list_all = AsyncMock(side_effect=Exception('boom'))

        with pytest.raises(HTTPException) as exc_info:
            await pokedex_service.fetch_all(trainer_id=trainer.id)
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
        pokedex_service.initialize_pokemon = AsyncMock(
            return_value=DummyPokedex(
                pokemon_id=pokemon.id,
                trainer_id=trainer.id,
                discovered=False,
            )
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
        pokedex_service.initialize_pokemon.assert_awaited_once_with(
            pokemon=pokemon,
            trainer_id=trainer.id,
            discovered=False,
        )

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
        pokedex_service.initialize_pokemon = AsyncMock(
            return_value=DummyPokedex(
                pokemon_id=pokemon_incomplete.id,
                trainer_id=trainer.id,
                discovered=False,
            )
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
        pokedex_service.initialize_pokemon.assert_awaited_once_with(
            pokemon=pokemon_incomplete,
            trainer_id=trainer.id,
            discovered=False,
        )

    @staticmethod
    @pytest.mark.asyncio
    async def test_refresh_returns_empty_list_for_empty_input(pokedex_service, trainer):
        """Should return an empty list when no pokemons are provided"""
        pokedex_service.repository.find_by_pokemon = AsyncMock()
        pokedex_service.initialize_pokemon = AsyncMock()

        result = await pokedex_service.refresh(
            trainer_id=trainer.id,
            pokemons=[],
        )

        assert result == []
        pokedex_service.repository.find_by_pokemon.assert_not_awaited()
        pokedex_service.initialize_pokemon.assert_not_awaited()

    @staticmethod
    @pytest.mark.asyncio
    async def test_refresh_returns_none_entry_when_initialize_fails(
        pokedex_service,
        trainer,
        pokemon,
    ):
        """Should return a None entry when initialize fails internally"""
        pokedex_service.repository.find_by_pokemon = AsyncMock(return_value=None)
        pokedex_service.initialize_pokemon = AsyncMock(return_value=None)

        result = await pokedex_service.refresh(
            trainer_id=trainer.id,
            pokemons=[pokemon],
        )

        assert result == [None]
        pokedex_service.initialize_pokemon.assert_awaited_once_with(
            pokemon=pokemon,
            trainer_id=trainer.id,
            discovered=False,
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


class TestPokedexServiceDiscovered:
    """Test scope for discovered method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_discovered_updates_when_not_discovered(pokedex_service, trainer, pokemon):
        """Should initialize and persist stats when entry is not discovered"""
        pokedex = DummyPokedex(discovered=False)
        pokedex_service.find_by_pokemon = AsyncMock(return_value=pokedex)
        pokedex_service.repository.update = AsyncMock(return_value=pokedex)

        result = await pokedex_service.discovered(
            trainer_id=trainer.id,
            pokemon=pokemon,
            discovered=True,
        )

        assert result is pokedex
        assert pokedex.discovered is True
        pokedex_service.repository.update.assert_awaited_once_with(pokedex)

    @staticmethod
    @pytest.mark.asyncio
    async def test_discovered_keeps_existing_discovered(pokedex_service, trainer, pokemon):
        """Should not update repository when already discovered"""
        pokedex = DummyPokedex(discovered=True)
        pokedex_service.find_by_pokemon = AsyncMock(return_value=pokedex)
        pokedex_service.repository.update = AsyncMock()

        result = await pokedex_service.discovered(
            trainer_id=trainer.id,
            pokemon=pokemon,
            discovered=True,
        )

        assert result is pokedex
        pokedex_service.repository.update.assert_not_awaited()


class TestPokedexServiceDiscover:
    """Test scope for discover method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_discover_updates_when_not_discovered(pokedex_service, trainer, pokemon):
        """Should discover pokemon and persist stats"""
        pokedex = DummyPokedex(discovered=False)
        pokedex_service.pokemon_service.fetch_one = AsyncMock(return_value=pokemon)
        pokedex_service.find_by_pokemon = AsyncMock(return_value=pokedex)
        pokedex_service.repository.update = AsyncMock(return_value=pokedex)

        result = await pokedex_service.discover(
            trainer_id=trainer.id,
            pokemon_name=pokemon.name,
        )

        assert result is pokedex
        assert pokedex.discovered is True
        pokedex_service.repository.update.assert_awaited_once_with(pokedex)

    @staticmethod
    @pytest.mark.asyncio
    async def test_discover_returns_same_when_already_discovered(
        pokedex_service, trainer, pokemon
    ):
        """Should return pokedex without updating when already discovered"""
        pokedex = DummyPokedex(discovered=True)
        pokedex_service.pokemon_service.fetch_one = AsyncMock(return_value=pokemon)
        pokedex_service.find_by_pokemon = AsyncMock(return_value=pokedex)
        pokedex_service.repository.update = AsyncMock()

        result = await pokedex_service.discover(
            trainer_id=trainer.id,
            pokemon_name=pokemon.name,
        )

        assert result is pokedex
        pokedex_service.repository.update.assert_not_awaited()


class TestPokedexServiceUpdate:
    """Test scope for update method"""

    EXPECTED_HP = 30
    EXPECTED_LEVEL = 2

    @staticmethod
    @pytest.mark.asyncio
    async def test_update_raises_not_found_when_missing(pokedex_service):
        """Should raise not found when pokedex entry does not exist"""
        pokedex_service.repository.find_by_id = AsyncMock(return_value=None)

        with pytest.raises(HTTPException) as exc_info:
            await pokedex_service.update(
                pokedex_id='missing-id',
                pokedex_update=DummyPokedex(model_dump=lambda: {'hp': 1}),
            )

        assert exc_info.value.status_code == HTTPStatus.NOT_FOUND
        assert exc_info.value.detail == 'Pokedex not found'

    @staticmethod
    @pytest.mark.asyncio
    async def test_update_applies_partial_values(pokedex_service):
        """Should apply partial values and persist"""
        pokedex = DummyPokedex(hp=10, level=1)
        pokedex_service.repository.find_by_id = AsyncMock(return_value=pokedex)
        pokedex_service.repository.update = AsyncMock(return_value=pokedex)

        update_schema = DummyPokedex(
            model_dump=lambda: {
                'hp': TestPokedexServiceUpdate.EXPECTED_HP,
                'level': TestPokedexServiceUpdate.EXPECTED_LEVEL,
            }
        )

        result = await pokedex_service.update(
            pokedex_id='pokedex-id',
            pokedex_update=update_schema,
        )

        assert result.hp == TestPokedexServiceUpdate.EXPECTED_HP
        assert result.level == TestPokedexServiceUpdate.EXPECTED_LEVEL
        pokedex_service.repository.update.assert_awaited_once_with(pokedex)


class TestPokedexServiceInitializePokemon:
    """Test scope for initialize_pokemon method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_initialize_pokemon_returns_none_on_error(pokedex_service, pokemon):
        """Should return None when repository create fails"""
        pokedex_service.repository.create = AsyncMock(side_effect=Exception('boom'))

        result = await pokedex_service.initialize_pokemon(
            pokemon=pokemon,
            trainer_id='trainer-id',
            discovered=False,
        )

        assert result is None
