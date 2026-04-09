from http import HTTPStatus
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from app.domain.pokedex.schema import GetWildPokemon, PartialPokedexSchema

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

    @staticmethod
    @pytest.mark.asyncio
    async def test_initialize_handles_none_existing_pokemon_ids(
        pokedex_service,
        trainer,
        pokemon,
    ):
        """Should treat None from repository.find_by as empty list and create entries."""
        created_entry = SimpleNamespace(
            pokemon_id=pokemon.id,
            trainer_id=trainer.id,
            discovered=True,
        )
        pokedex_service.repository.find_by = AsyncMock(return_value=None)
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
                param='missing-id',
                update_schema=PartialPokedexSchema(hp=1),
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
            param='pokedex-id',
            update_schema=PartialPokedexSchema(hp=MOCK_UPDATED_HP),
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

    @staticmethod
    @pytest.mark.asyncio
    async def test_initialize_pokemon_sets_discovered_at_when_discovered_true(
        pokedex_service, pokemon, trainer
    ):
        """Should set discovered_at when discovered is True."""

        result = await pokedex_service.initialize_pokemon(
            pokemon=pokemon,
            trainer_id=trainer.id,
            discovered=True,
        )

        assert result.discovered_at is not None


class TestPokedexServiceGetWildPokemon:
    """Test scope for get_wild_pokemon method."""

    @staticmethod
    @pytest.mark.asyncio
    async def test_get_wild_pokemon_returns_none_when_not_found(pokedex_service):
        """Should return None when pokedex is not found."""
        pokedex_service.pokemon_service.random_pokemon_by_filter = AsyncMock(return_value=None)
        with pytest.raises(HTTPException) as exc_info:
            await pokedex_service.get_wild_pokemon(
                params=GetWildPokemon(habitat='grass'),
                trainer_id='trainer-id',
                user_request=None,
            )
        assert exc_info.value.status_code == HTTPStatus.NOT_FOUND
        assert exc_info.value.detail == (
            'No wild pokemon found! Try changing the habitat or try again later.'
        )

    @staticmethod
    @pytest.mark.asyncio
    async def test_get_wild_pokemon_returns_pokedex(pokedex_service, pokedex, pokemon):
        """Should return None when pokedex is not found."""
        pokedex_service.pokemon_service.random_pokemon_by_filter = AsyncMock(
            return_value=pokemon
        )
        pokedex_service.discovered = AsyncMock(return_value=pokedex)
        result = await pokedex_service.get_wild_pokemon(
            params=GetWildPokemon(habitat='grass'), trainer_id='trainer-id', user_request=None
        )
        assert result is not None
        assert result.nickname == pokedex.nickname
