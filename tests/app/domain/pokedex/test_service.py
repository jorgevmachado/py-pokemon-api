from unittest.mock import AsyncMock, MagicMock, patch

import pytest

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
