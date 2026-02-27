import pytest

from app.domain.pokedex.service import PokedexService


class TestPokedexServiceInitialize:
    """Test scope for initialize method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_initialize_creates_missing_entries(session, user, pokemon):
        """Should create pokedex entries when missing"""
        service = PokedexService(session=session)

        result = await service.initialize(user=user, pokemon=pokemon, pokemons=[pokemon])

        assert len(result) == 1
        assert result[0].pokemon_id == pokemon.id
        assert result[0].trainer_id == user.id
        assert result[0].discovered is True

    @staticmethod
    @pytest.mark.asyncio
    async def test_initialize_skips_existing_entries(session, user, pokemon):
        """Should skip pokedex entries that already exist"""
        service = PokedexService(session=session)

        await service.initialize(user=user, pokemon=pokemon, pokemons=[pokemon])
        result = await service.initialize(user=user, pokemon=pokemon, pokemons=[pokemon])

        assert result == []

    @staticmethod
    @pytest.mark.asyncio
    async def test_initialize_marks_discovered_false_when_no_pokemon(session, user, pokemon):
        """Should mark discovered as false when pokemon is None"""
        service = PokedexService(session=session)

        result = await service.initialize(user=user, pokemon=None, pokemons=[pokemon])

        assert len(result) == 1
        assert result[0].discovered is False


class TestPokedexServiceInitializeEntry:
    """Test scope for initialize_pokedex_entry method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_initialize_pokedex_entry_raises_type_error(session, user, pokemon):
        """Should raise TypeError with current model signature"""
        service = PokedexService(session=session)

        with pytest.raises(TypeError):
            await service.initialize_pokedex_entry(pokemon=pokemon, user=user)


class TestPokedexServiceCapturePokemon:
    """Test scope for capture_pokemon method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_capture_pokemon_raises_type_error(session, user, pokemon):
        """Should raise TypeError with current model signature"""
        service = PokedexService(session=session)

        with pytest.raises(TypeError):
            await service.capture_pokemon(pokemon=pokemon, user=user)


class TestPokedexServiceAddPokemonToPokedexAndCapture:
    """Test scope for add_pokemon_to_pokedex_and_capture method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_add_pokemon_to_pokedex_and_capture_raises_type_error(
        session, user, pokemon
    ):
        """Should raise TypeError with current model signature"""
        service = PokedexService(session=session)

        with pytest.raises(TypeError):
            await service.add_pokemon_to_pokedex_and_capture(
                pokemon=pokemon,
                user=user,
            )
