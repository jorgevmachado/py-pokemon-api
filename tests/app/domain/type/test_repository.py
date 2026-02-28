from unittest.mock import AsyncMock

import pytest

from app.domain.type.model import PokemonType
from app.domain.type.repository import PokemonTypeRepository
from app.domain.type.schema import CreatePokemonTypeSchema


class TestPokemonTypeRepositoryCreate:
    """Test scope for create method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_type_repository_create_success(session):
        """Should persist pokemon type when data is valid"""
        pokemon_type_data_order = 133
        pokemon_type_data = CreatePokemonTypeSchema(
            url='https://pokeapi.co/api/v2/type/12/',
            name='fire',
            order=pokemon_type_data_order,
            text_color='#fff',
            background_color='#fd7d24',
        )
        repository = PokemonTypeRepository(session=session)
        pokemon_type = await repository.create(pokemon_type_data)
        assert pokemon_type.url == 'https://pokeapi.co/api/v2/type/12/'
        assert pokemon_type.name == 'fire'
        assert pokemon_type.order == pokemon_type_data_order
        assert pokemon_type.text_color == '#fff'
        assert pokemon_type.background_color == '#fd7d24'

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_type_repository_create_commit_error(session):
        """Should persist pokemon type when data is valid"""
        pokemon_type_data_order = 133
        pokemon_type_data = CreatePokemonTypeSchema(
            url='https://pokeapi.co/api/v2/type/12/',
            name='fire',
            order=pokemon_type_data_order,
            text_color='#fff',
            background_color='#fd7d24',
        )
        session.commit = AsyncMock(side_effect=Exception('Database error'))

        repository = PokemonTypeRepository(session=session)

        with pytest.raises(Exception, match='Database error'):
            await repository.create(pokemon_type_data)


class TestPokemonTypeRepositoryFindOneByOrder:
    """Test scope for find one by order method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_type_repository_find_one_not_found(session):
        """Should return None when pokemonType is not found"""

        repository = PokemonTypeRepository(session=session)
        result = await repository.find_one_by_order(1)
        assert result is None

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_type_repository_find_one_by_order_success(session):
        """Should return pokemon type when found by order"""
        result_order = 1

        pokemon_type = PokemonType(
            url='https://pokeapi.co/api/v2/type/12/',
            name='fire',
            order=result_order,
            text_color='#fff',
            background_color='#fd7d24',
        )
        session.add(pokemon_type)
        await session.commit()

        repository = PokemonTypeRepository(session=session)

        result = await repository.find_one_by_order(result_order)
        assert result is not None
        assert isinstance(result, PokemonType)
        assert result.order == result_order


class TestPokemonTypeRepositoryFindOneByName:
    """Test scope for find one by name method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_type_repository_find_one_by_name_not_found(session):
        """Should return None when pokemonType is not found"""

        repository = PokemonTypeRepository(session=session)
        result = await repository.find_one(name='name')
        assert result is None

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_type_repository_find_one_by_name_success(session):
        """Should return pokemon type when found by order"""
        result_order = 1

        pokemon_type = PokemonType(
            url='https://pokeapi.co/api/v2/type/12/',
            name='fire',
            order=result_order,
            text_color='#fff',
            background_color='#fd7d24',
        )
        session.add(pokemon_type)
        await session.commit()

        repository = PokemonTypeRepository(session=session)

        result = await repository.find_one(name=pokemon_type.name)
        assert result is not None
        assert isinstance(result, PokemonType)
        assert result.order == result_order
        assert result.name == pokemon_type.name
