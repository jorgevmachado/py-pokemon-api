from unittest.mock import AsyncMock

import pytest

from app.domain.type.model import PokemonType


class TestPokemonTypeRepositorySave:
    """Test scope for save method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_type_repository_save_success(pokemon_type_repository):
        """Should persist pokemon type when data is valid"""
        pokemon_type_data_order = 133

        pokemon_type = await pokemon_type_repository.save(
            entity=PokemonType(
                url='https://pokeapi.co/api/v2/type/12/',
                name='fire',
                order=pokemon_type_data_order,
                text_color='#fff',
                background_color='#fd7d24',
            )
        )
        assert pokemon_type.url == 'https://pokeapi.co/api/v2/type/12/'
        assert pokemon_type.name == 'fire'
        assert pokemon_type.order == pokemon_type_data_order
        assert pokemon_type.text_color == '#fff'
        assert pokemon_type.background_color == '#fd7d24'

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_type_repository_save_commit_error(session, pokemon_type_repository):
        """Should persist pokemon type when data is valid"""
        pokemon_type_data_order = 133
        session.commit = AsyncMock(side_effect=Exception('Database error'))

        with pytest.raises(Exception, match='Database error'):
            await pokemon_type_repository.save(
                entity=PokemonType(
                    url='https://pokeapi.co/api/v2/type/12/',
                    name='fire',
                    order=pokemon_type_data_order,
                    text_color='#fff',
                    background_color='#fd7d24',
                )
            )


class TestPokemonTypeRepositoryFindBy:
    """Test scope for find by method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_type_repository_find_by_not_found(pokemon_type_repository):
        """Should return None when pokemonType is not found"""

        result = await pokemon_type_repository.find_by(order=1)
        assert result is None

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_type_repository_find_by_order_success(
        pokemon_type, pokemon_type_repository
    ):
        """Should return pokemon type when found by order"""

        result = await pokemon_type_repository.find_by(order=pokemon_type.order)
        assert result is not None
        assert isinstance(result, PokemonType)
        assert result.order == pokemon_type.order

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_type_repository_find_by_name_not_found(pokemon_type_repository):
        """Should return None when pokemonType is not found"""
        result = await pokemon_type_repository.find_by(name='name')
        assert result is None

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_type_repository_find_by_name_success(
        pokemon_type, pokemon_type_repository
    ):
        """Should return pokemon type when found by name"""

        result = await pokemon_type_repository.find_by(name=pokemon_type.name)
        assert result is not None
        assert isinstance(result, PokemonType)
        assert result.order == pokemon_type.order
        assert result.name == pokemon_type.name


class TestPokemonTypeRepositoryUpdate:
    """Test scope for update method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_type_repository_update_success(
        pokemon_type, pokemon_type_repository
    ):
        """Should update pokemon type when data is valid"""
        result = await pokemon_type_repository.update(pokemon_type)
        assert result.name == 'fire'

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_type_repository_update_commit_error(
        session, pokemon_type, pokemon_type_repository
    ):
        """Should raise exception when commit fails during update"""
        session.commit = AsyncMock(side_effect=Exception('Database error'))

        with pytest.raises(Exception, match='Database error'):
            await pokemon_type_repository.update(pokemon_type)
