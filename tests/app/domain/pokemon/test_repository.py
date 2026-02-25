import random
from unittest.mock import AsyncMock

import factory
import pytest
from factory import Faker

from app.domain.pokemon.repository import PokemonRepository
from app.domain.pokemon.schema import CreatePokemonSchema
from app.models import Pokemon
from app.shared.schemas import FilterPage
from app.shared.status_enum import StatusEnum
from tests.app.domain.pokemon.mock import MOCK_ENTITY_POKEMON


class PokemonFactory(factory.Factory):
    class Meta:
        model = Pokemon

    url = factory.LazyAttribute(lambda o: f'https://pokeapi.co/api/v2/pokemon/{o.name}')
    name = Faker('name')
    order = factory.Sequence(lambda n: n)
    status = StatusEnum.COMPLETE
    external_image = factory.LazyAttribute(
        lambda o: f'https://pokeapi.co/api/v2/pokemon/{o.name}'
    )
    hp = factory.Sequence(lambda n: n * 45)
    image = factory.LazyAttribute(lambda o: f'https://pokeapi.co/api/v2/pokemon/{o.name}')
    speed = factory.Sequence(lambda n: n * 45)
    height = factory.Sequence(lambda n: n * 7)
    weight = factory.Sequence(lambda n: n * 69)
    attack = factory.Sequence(lambda n: n * 49)
    defense = factory.Sequence(lambda n: n * 65)
    habitat = 'grassland'
    is_baby = factory.LazyAttribute(lambda o: random.choice([True, False]))
    shape_url = factory.LazyAttribute(lambda o: f'https://pokeapi.co/api/v2/pokemon/{o.name}')
    shape_name = factory.LazyAttribute(lambda o: f'shape_name_{o.name}')
    is_mythical = factory.LazyAttribute(lambda o: random.choice([True, False]))
    gender_rate = factory.Sequence(lambda n: n * 1)
    is_legendary = factory.LazyAttribute(lambda o: random.choice([True, False]))
    capture_rate = factory.Sequence(lambda n: n * 69)
    hatch_counter = factory.Sequence(lambda n: n * 69)
    base_happiness = factory.Sequence(lambda n: n * 69)
    special_attack = factory.Sequence(lambda n: n * 65)
    base_experience = factory.Sequence(lambda n: n * 64)
    special_defense = factory.Sequence(lambda n: n * 65)
    evolution_chain_url = factory.LazyAttribute(
        lambda o: f'https://pokeapi.co/api/v2/pokemon/{o.name}'
    )
    evolves_from_species = factory.LazyAttribute(lambda o: f'evolves_from_species_{o.name}')
    has_gender_differences = factory.LazyAttribute(lambda o: random.choice([True, False]))


class TestPokemonRepositoryTotal:
    """Test scope for total method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_repository_total_success():
        """Should return total pokemon count when query is successful"""
        expected_total = 10
        mock_session = AsyncMock()
        mock_session.scalar = AsyncMock(return_value=expected_total)

        repository = PokemonRepository(session=mock_session)
        result = await repository.total()

        assert result == expected_total
        mock_session.scalar.assert_called_once()

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_repository_total_empty():
        """Should return zero when no pokemon exists"""
        expected_total = 0
        mock_session = AsyncMock()
        mock_session.scalar = AsyncMock(return_value=expected_total)

        repository = PokemonRepository(session=mock_session)
        result = await repository.total()

        assert result == expected_total
        mock_session.scalar.assert_called_once()

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_repository_total_large_number():
        """Should return correct count for large number of pokemon"""
        expected_total = 1025
        mock_session = AsyncMock()
        mock_session.scalar = AsyncMock(return_value=expected_total)

        repository = PokemonRepository(session=mock_session)
        result = await repository.total()

        assert result == expected_total
        assert isinstance(result, int)
        mock_session.scalar.assert_called_once()

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_repository_total_database_error():
        """Should raise exception when database query fails"""
        mock_session = AsyncMock()
        mock_session.scalar = AsyncMock(side_effect=Exception('Database error'))

        repository = PokemonRepository(session=mock_session)

        with pytest.raises(Exception, match='Database error'):
            await repository.total()

        mock_session.scalar.assert_called_once()


class TestPokemonRepositoryList:
    """Test scope for list method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_repository_list_success(session):
        """Should return list of pokemon when query is successful"""
        pokemon1 = MOCK_ENTITY_POKEMON
        session.add(pokemon1)
        await session.commit()
        await session.refresh(pokemon1)

        repository = PokemonRepository(session=session)
        result = await repository.list()

        assert isinstance(result, list)
        assert len(result) >= 1

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_repository_list_empty(session):
        """Should return empty list when no pokemon exists"""
        repository = PokemonRepository(session=session)
        result = await repository.list()

        assert isinstance(result, list)
        assert len(result) == 0

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_repository_list_with_offset(session):
        """Should apply offset filter correctly"""
        total_result = 3

        for _ in range(5):
            pokemon = PokemonFactory()
            session.add(pokemon)
            await session.commit()

        repository = PokemonRepository(session=session)
        result = await repository.list(pokemon_filter=FilterPage(offset=2, limit=10))

        assert isinstance(result, list)
        assert len(result) == total_result

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_repository_list_with_limit(session):
        """Should apply limit filter correctly"""
        total_result = 2

        for _ in range(5):
            pokemon = PokemonFactory()
            session.add(pokemon)
            await session.commit()

        repository = PokemonRepository(session=session)
        result = await repository.list(pokemon_filter=FilterPage(offset=0, limit=2))

        assert isinstance(result, list)
        assert len(result) == total_result

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_repository_list_with_offset_and_limit(session):
        """Should apply both offset and limit correctly"""
        total_result = 4

        for _ in range(10):
            pokemon = PokemonFactory()
            session.add(pokemon)
            await session.commit()

        repository = PokemonRepository(session=session)
        result = await repository.list(pokemon_filter=FilterPage(offset=3, limit=4))

        assert isinstance(result, list)
        assert len(result) == total_result


class TestPokemonRepositoryFindOne:
    """Test scope for find one method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_repository_find_one_success(session):
        """Should return pokemon when found by name"""
        pokemon = PokemonFactory(name='Pikachu')
        session.add(pokemon)
        await session.commit()

        repository = PokemonRepository(session=session)
        result = await repository.find_one(name='Pikachu')

        assert result is not None
        assert isinstance(result, Pokemon)
        assert result.name == 'Pikachu'

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_repository_find_one_not_found(session):
        """Should return None when pokemon is not found"""
        repository = PokemonRepository(session=session)
        result = await repository.find_one(name='NonExistentPokemon')

        assert result is None

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_repository_find_one_with_related_data(session):
        """Should load pokemon with all related relationships"""
        pokemon = PokemonFactory(name='Charizard')
        session.add(pokemon)
        await session.commit()

        repository = PokemonRepository(session=session)
        result = await repository.find_one(name='Charizard')

        assert result is not None
        assert result.name == 'Charizard'
        assert hasattr(result, 'growth_rate')
        assert hasattr(result, 'moves')
        assert hasattr(result, 'types')
        assert hasattr(result, 'abilities')
        assert hasattr(result, 'evolutions')

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_repository_find_one_case_sensitive(session):
        """Should match pokemon name with exact case"""
        pokemon = PokemonFactory(name='bulbasaur')
        session.add(pokemon)
        await session.commit()

        repository = PokemonRepository(session=session)
        result = await repository.find_one(name='bulbasaur')

        assert result is not None
        assert result.name == 'bulbasaur'

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_repository_find_one_case_mismatch(session):
        """Should return None when pokemon name case does not match"""
        pokemon = PokemonFactory(name='Squirtle')
        session.add(pokemon)
        await session.commit()

        repository = PokemonRepository(session=session)
        result = await repository.find_one(name='squirtle')

        assert result is None

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_repository_find_one_database_error():
        """Should raise exception when database query fails"""
        mock_session = AsyncMock()
        mock_session.scalar = AsyncMock(side_effect=Exception('Database error'))

        repository = PokemonRepository(session=mock_session)

        with pytest.raises(Exception, match='Database error'):
            await repository.find_one(name='AnyPokemon')

        mock_session.scalar.assert_called_once()

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_repository_find_one_empty_string_name(session):
        """Should return None when searching with empty string"""
        pokemon = PokemonFactory(name='Venusaur')
        session.add(pokemon)
        await session.commit()

        repository = PokemonRepository(session=session)
        result = await repository.find_one(name='')

        assert result is None

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_repository_find_one_with_special_characters(session):
        """Should find pokemon with special characters in name"""
        pokemon = PokemonFactory(name='Nidoran♂')
        session.add(pokemon)
        await session.commit()

        repository = PokemonRepository(session=session)
        result = await repository.find_one(name='Nidoran♂')

        assert result is not None
        assert result.name == 'Nidoran♂'


class TestPokemonRepositoryCreate:
    """Test scope for create method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_repository_create_success(session):
        """Should persist pokemon with default status when data is valid"""
        pokemon_data_order = 133
        pokemon_data = CreatePokemonSchema(
            name='Eevee',
            order=pokemon_data_order,
            url='https://pokeapi.co/api/v2/pokemon/eevee',
            external_image='https://pokeapi.co/api/v2/pokemon/eevee',
        )

        repository = PokemonRepository(session=session)
        result = await repository.create(pokemon_data=pokemon_data)

        assert isinstance(result, Pokemon)
        assert result.name == 'Eevee'
        assert result.order == pokemon_data_order
        assert result.url == 'https://pokeapi.co/api/v2/pokemon/eevee'
        assert result.external_image == 'https://pokeapi.co/api/v2/pokemon/eevee'
        assert result.status == StatusEnum.INCOMPLETE

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_repository_create_commit_error(session):
        """Should raise exception when commit fails"""
        pokemon_data = CreatePokemonSchema(
            name='Mew',
            order=151,
            url='https://pokeapi.co/api/v2/pokemon/mew',
            external_image='https://pokeapi.co/api/v2/pokemon/mew',
        )
        session.commit = AsyncMock(side_effect=Exception('Database error'))

        repository = PokemonRepository(session=session)

        with pytest.raises(Exception, match='Database error'):
            await repository.create(pokemon_data=pokemon_data)
