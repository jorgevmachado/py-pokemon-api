from http import HTTPStatus
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from app.domain.pokedex.schema import PartialPokedexSchema

MOCK_REFRESH_CALL_COUNT = 2
MOCK_UPDATED_HP = 30


class TestPokedexServiceInitialize:
    """Test scope for initialize method."""

    @staticmethod
    @pytest.mark.asyncio
    async def test_initialize_creates_missing_entries(
        pokedex_service,
        trainer,
        pokemon,
    ):
        """Should create entries for pokemons not present in trainer pokedex."""
        created_entry = SimpleNamespace(
            pokemon_id=pokemon.id,
            trainer_id=trainer.id,
            discovered=True,
        )
        pokedex_service.repository.find_by = AsyncMock(return_value=set())
        pokedex_service.initialize_pokemon = AsyncMock(return_value=created_entry)

        result = await pokedex_service.initialize(
            trainer=trainer,
            pokemon=pokemon,
            pokemons=[pokemon],
        )

        assert result == [created_entry]
        pokedex_service.repository.find_by.assert_awaited_once_with(trainer_id=trainer.id)
        pokedex_service.initialize_pokemon.assert_awaited_once_with(
            pokemon=pokemon,
            trainer_id=trainer.id,
            discovered=True,
        )

    @staticmethod
    @pytest.mark.asyncio
    async def test_initialize_skips_existing_entries(
        pokedex_service,
        trainer,
        pokemon,
    ):
        """Should not create entries for pokemons already present in trainer pokedex."""
        pokedex_service.repository.find_by = AsyncMock(return_value={pokemon.id})
        pokedex_service.initialize_pokemon = AsyncMock()

        result = await pokedex_service.initialize(
            trainer=trainer,
            pokemon=pokemon,
            pokemons=[pokemon],
        )

        assert result == []
        pokedex_service.initialize_pokemon.assert_not_awaited()

    @staticmethod
    @pytest.mark.asyncio
    async def test_initialize_returns_empty_on_repository_error(
        pokedex_service,
        trainer,
        pokemon,
    ):
        """Should return empty list when repository fails in initialize flow."""
        pokedex_service.repository.find_by = AsyncMock(side_effect=Exception('boom'))

        result = await pokedex_service.initialize(
            trainer=trainer,
            pokemon=pokemon,
            pokemons=[pokemon],
        )

        assert result == []


class TestPokedexServiceFetchAll:
    """Test scope for fetch_all method."""

    @staticmethod
    @pytest.mark.asyncio
    async def test_fetch_all_passes_trainer_filter(pokedex_service, trainer):
        """Should pass trainer_id merged into page_filter when listing pokedex."""
        expected_result = ['entry']
        pokedex_service.repository.list_all = AsyncMock(return_value=expected_result)

        result = await pokedex_service.fetch_all(trainer_id=trainer.id)

        assert result == expected_result
        pokedex_service.repository.list_all.assert_awaited_once()
        call_args = pokedex_service.repository.list_all.await_args.kwargs
        page_filter = call_args['page_filter']
        assert page_filter.model_dump(exclude_none=True) == {'trainer_id': trainer.id}

    @staticmethod
    @pytest.mark.asyncio
    async def test_fetch_all_raises_http_exception_on_repository_error(
        pokedex_service,
        trainer,
    ):
        """Should raise HTTPException when repository fails."""
        pokedex_service.repository.list_all = AsyncMock(side_effect=Exception('boom'))

        with pytest.raises(HTTPException) as exc_info:
            await pokedex_service.fetch_all(trainer_id=trainer.id)

        assert exc_info.value.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert exc_info.value.detail == 'Internal server error'


class TestPokedexServiceRefresh:
    """Test scope for refresh method."""

    @staticmethod
    @pytest.mark.asyncio
    async def test_refresh_creates_entries_for_missing_pokemon(
        pokedex_service,
        trainer,
        pokemon,
    ):
        """Should create one entry when pokemon is not found in pokedex."""
        created_entry = SimpleNamespace(
            pokemon_id=pokemon.id,
            trainer_id=trainer.id,
            discovered=False,
        )
        pokedex_service.repository.find_by = AsyncMock(return_value=None)
        pokedex_service.initialize_pokemon = AsyncMock(return_value=created_entry)

        result = await pokedex_service.refresh(trainer_id=trainer.id, pokemons=[pokemon])

        assert result == [created_entry]
        pokedex_service.repository.find_by.assert_awaited_once_with(
            trainer_id=trainer.id,
            pokemon_id=pokemon.id,
        )

    @staticmethod
    @pytest.mark.asyncio
    async def test_refresh_skips_existing_entries(
        pokedex_service,
        trainer,
        pokemon,
        pokemon_incomplete,
    ):
        """Should create only entries for pokemons not found in pokedex."""
        created_entry = SimpleNamespace(
            pokemon_id=pokemon_incomplete.id,
            trainer_id=trainer.id,
            discovered=False,
        )
        pokedex_service.repository.find_by = AsyncMock(
            side_effect=[SimpleNamespace(pokemon_id=pokemon.id), None]
        )
        pokedex_service.initialize_pokemon = AsyncMock(return_value=created_entry)

        result = await pokedex_service.refresh(
            trainer_id=trainer.id,
            pokemons=[pokemon, pokemon_incomplete],
        )

        assert result == [created_entry]
        assert pokedex_service.repository.find_by.await_count == MOCK_REFRESH_CALL_COUNT
        pokedex_service.initialize_pokemon.assert_awaited_once_with(
            pokemon=pokemon_incomplete,
            trainer_id=trainer.id,
            discovered=False,
        )


class TestPokedexServiceFindBy:
    """Test scope for find_by wrapper method."""

    @staticmethod
    @pytest.mark.asyncio
    async def test_find_by_returns_repository_result(pokedex_service, trainer, pokemon):
        """Should proxy kwargs to repository.find_by and return its result."""
        expected_result = {'pokemon_id': pokemon.id, 'trainer_id': trainer.id}
        pokedex_service.repository.find_by = AsyncMock(return_value=expected_result)

        result = await pokedex_service.find_by(trainer_id=trainer.id, pokemon_id=pokemon.id)

        assert result == expected_result
        pokedex_service.repository.find_by.assert_awaited_once_with(
            trainer_id=trainer.id,
            pokemon_id=pokemon.id,
        )

    @staticmethod
    @pytest.mark.asyncio
    async def test_find_by_raises_http_exception_on_repository_error(
        pokedex_service, trainer, pokemon
    ):
        """Should raise HTTPException when repository raises an unexpected error."""
        pokedex_service.repository.find_by = AsyncMock(side_effect=Exception('boom'))

        with pytest.raises(HTTPException) as exc_info:
            await pokedex_service.find_by(trainer_id=trainer.id, pokemon_id=pokemon.id)

        assert exc_info.value.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert exc_info.value.detail == 'Internal server error'


class TestPokedexServiceDiscovered:
    """Test scope for discovered method."""

    @staticmethod
    @pytest.mark.asyncio
    async def test_discovered_updates_entry_when_not_discovered(
        pokedex_service,
        trainer,
        pokemon,
    ):
        """Should persist discovered updates when entry is not discovered yet."""
        pokedex = SimpleNamespace(discovered=False)
        pokedex_service.find_by = AsyncMock(return_value=pokedex)
        pokedex_service.repository.update = AsyncMock(return_value=pokedex)

        result = await pokedex_service.discovered(
            trainer_id=trainer.id,
            pokemon=pokemon,
            discovered=True,
        )

        assert result is pokedex
        assert result.discovered is True
        pokedex_service.repository.update.assert_awaited_once_with(pokedex)

    @staticmethod
    @pytest.mark.asyncio
    async def test_discovered_keeps_entry_when_already_discovered(
        pokedex_service,
        trainer,
        pokemon,
    ):
        """Should not call repository.update when entry is already discovered."""
        pokedex = SimpleNamespace(discovered=True)
        pokedex_service.find_by = AsyncMock(return_value=pokedex)
        pokedex_service.repository.update = AsyncMock()

        result = await pokedex_service.discovered(
            trainer_id=trainer.id,
            pokemon=pokemon,
            discovered=True,
        )

        assert result is pokedex
        pokedex_service.repository.update.assert_not_awaited()


class TestPokedexServiceDiscover:
    """Test scope for discover method."""

    @staticmethod
    @pytest.mark.asyncio
    async def test_discover_updates_entry_when_not_discovered(
        pokedex_service,
        trainer,
        pokemon,
    ):
        """Should discover pokemon and persist updates when entry is not discovered."""
        pokedex = SimpleNamespace(discovered=False)
        pokedex_service.pokemon_service.fetch_one = AsyncMock(return_value=pokemon)
        pokedex_service.find_by = AsyncMock(return_value=pokedex)
        pokedex_service.repository.update = AsyncMock(return_value=pokedex)

        result = await pokedex_service.discover(
            trainer_id=trainer.id,
            pokemon_name=pokemon.name,
        )

        assert result is pokedex
        assert result.discovered is True
        pokedex_service.repository.update.assert_awaited_once_with(pokedex)

    @staticmethod
    @pytest.mark.asyncio
    async def test_discover_skips_update_when_already_discovered(
        pokedex_service,
        trainer,
        pokemon,
    ):
        """Should return pokedex without updating when pokemon is already discovered."""
        pokedex = SimpleNamespace(discovered=True)
        pokedex_service.pokemon_service.fetch_one = AsyncMock(return_value=pokemon)
        pokedex_service.find_by = AsyncMock(return_value=pokedex)
        pokedex_service.repository.update = AsyncMock()

        result = await pokedex_service.discover(
            trainer_id=trainer.id,
            pokemon_name=pokemon.name,
        )

        assert result is pokedex
        assert result.discovered is True
        pokedex_service.repository.update.assert_not_awaited()


class TestPokedexServiceUpdate:
    """Test scope for update method."""

    @staticmethod
    @pytest.mark.asyncio
    async def test_update_raises_not_found_when_missing(pokedex_service):
        """Should raise not found when pokedex entry does not exist."""
        pokedex_service.repository.find_by = AsyncMock(return_value=None)

        with pytest.raises(HTTPException) as exc_info:
            await pokedex_service.update(
                pokedex_id='missing-id',
                pokedex_update=PartialPokedexSchema(hp=1),
            )

        assert exc_info.value.status_code == HTTPStatus.NOT_FOUND
        assert exc_info.value.detail == 'Pokedex not found'

    @staticmethod
    @pytest.mark.asyncio
    async def test_update_applies_partial_values(pokedex_service):
        """Should apply partial values and persist update."""
        pokedex = SimpleNamespace(hp=10)
        pokedex_service.repository.find_by = AsyncMock(return_value=pokedex)
        pokedex_service.repository.update = AsyncMock(return_value=pokedex)

        result = await pokedex_service.update(
            pokedex_id='pokedex-id',
            pokedex_update=PartialPokedexSchema(hp=MOCK_UPDATED_HP),
        )

        assert result.hp == MOCK_UPDATED_HP
        pokedex_service.repository.update.assert_awaited_once_with(pokedex)


class TestPokedexServiceInitializePokemon:
    """Test scope for initialize_pokemon method."""

    @staticmethod
    @pytest.mark.asyncio
    async def test_initialize_pokemon_returns_none_on_error(pokedex_service, pokemon):
        """Should return None when repository save fails."""
        pokedex_service.repository.save = AsyncMock(side_effect=Exception('boom'))

        result = await pokedex_service.initialize_pokemon(
            pokemon=pokemon,
            trainer_id='trainer-id',
            discovered=False,
        )

        assert result is None
