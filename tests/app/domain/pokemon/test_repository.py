from unittest.mock import AsyncMock

import pytest

from app.domain.pokemon.model import Pokemon
from app.domain.pokemon.repository import PokemonRepository
from app.domain.pokemon.schema import CreatePokemonSchema
from app.shared.schemas import FilterPage
from app.shared.status_enum import StatusEnum
from tests.app.domain.pokemon.mock import MOCK_ENTITY_POKEMON
from tests.factories.pokemon import PokemonFactory

MOCK_PIKACHU_HP = 35
MOCK_PIKACHU_ATTACK = 55
MOCK_CHARIZARD_HP = 78
MOCK_CHARIZARD_ATTACK = 84
MOCK_CHARIZARD_DEFENSE = 78
MOCK_CHARIZARD_SPECIAL_ATTACK = 109
MOCK_CHARIZARD_SPECIAL_DEFENSE = 85
MOCK_CHARIZARD_SPEED = 100
MOCK_CHARIZARD_HEIGHT = 17
MOCK_CHARIZARD_WEIGHT = 905
MOCK_SQUIRTLE_HP = 44


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
    """Test scope for list_all method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_repository_list_success(session):
        """Should return list of pokemon when query is successful"""
        pokemon1 = MOCK_ENTITY_POKEMON
        session.add(pokemon1)
        await session.commit()
        await session.refresh(pokemon1)

        repository = PokemonRepository(session=session)
        result = await repository.list_all()

        assert isinstance(result, list)
        assert len(result) >= 1

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_repository_list_empty(session):
        """Should return empty list when no pokemon exists"""
        repository = PokemonRepository(session=session)
        result = await repository.list_all()

        assert isinstance(result, list)
        assert len(result) == 0

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_repository_list_with_offset(session):
        """Should apply offset filter correctly"""

        for _ in range(5):
            pokemon = PokemonFactory()
            session.add(pokemon)
            await session.commit()

        repository = PokemonRepository(session=session)
        page_filter = FilterPage(offset=2, limit=10)
        result = await repository.list_all(page_filter=page_filter)

        assert result is not None
        # Com paginação, retorna LimitOffsetPage
        assert hasattr(result, 'items') or isinstance(result, list)

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
        page_filter = FilterPage(offset=0, limit=2)
        result = await repository.list_all(page_filter=page_filter)

        assert result is not None
        # Com paginação, retorna LimitOffsetPage
        if hasattr(result, 'items'):
            assert len(result.items) == total_result
        else:
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
        page_filter = FilterPage(offset=3, limit=4)
        result = await repository.list_all(page_filter=page_filter)

        assert result is not None
        # Com paginação, retorna LimitOffsetPage
        if hasattr(result, 'items'):
            assert len(result.items) == total_result
        else:
            assert len(result) == total_result

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_repository_list_without_pagination(session):
        """Should return plain list when no pagination params provided"""
        total_result = 3
        for _ in range(3):
            pokemon = PokemonFactory()
            session.add(pokemon)
            await session.commit()

        repository = PokemonRepository(session=session)
        result = await repository.list_all(page_filter=None)

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


class TestPokemonRepositoryUpdate:
    """Test scope for update method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_repository_update_success(session):
        """Should update pokemon successfully when data is valid"""
        pokemon = Pokemon(
            name='Pikachu',
            order=25,
            url='https://pokeapi.co/api/v2/pokemon/25/',
            status=StatusEnum.INCOMPLETE,
            external_image='https://pokeapi.co/api/v2/pokemon/25/image.png',
        )
        session.add(pokemon)
        await session.commit()
        await session.refresh(pokemon)

        pokemon.status = StatusEnum.COMPLETE
        pokemon.hp = MOCK_PIKACHU_HP
        pokemon.attack = MOCK_PIKACHU_ATTACK

        repository = PokemonRepository(session=session)
        result = await repository.update(pokemon=pokemon)

        assert result.status == StatusEnum.COMPLETE
        assert result.hp == MOCK_PIKACHU_HP
        assert result.attack == MOCK_PIKACHU_ATTACK
        assert result.name == 'Pikachu'

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_repository_update_all_attributes(session):
        """Should update all pokemon attributes correctly"""
        pokemon = Pokemon(
            name='Charizard',
            order=6,
            url='https://pokeapi.co/api/v2/pokemon/6/',
            status=StatusEnum.INCOMPLETE,
            external_image='https://pokeapi.co/api/v2/pokemon/6/image.png',
        )
        session.add(pokemon)
        await session.commit()
        await session.refresh(pokemon)

        pokemon.status = StatusEnum.COMPLETE
        pokemon.hp = MOCK_CHARIZARD_HP
        pokemon.attack = MOCK_CHARIZARD_ATTACK
        pokemon.defense = MOCK_CHARIZARD_DEFENSE
        pokemon.special_attack = MOCK_CHARIZARD_SPECIAL_ATTACK
        pokemon.special_defense = MOCK_CHARIZARD_SPECIAL_DEFENSE
        pokemon.speed = MOCK_CHARIZARD_SPEED
        pokemon.height = MOCK_CHARIZARD_HEIGHT
        pokemon.weight = MOCK_CHARIZARD_WEIGHT
        pokemon.habitat = 'mountain'

        repository = PokemonRepository(session=session)
        result = await repository.update(pokemon=pokemon)

        assert result.status == StatusEnum.COMPLETE
        assert result.hp == MOCK_CHARIZARD_HP
        assert result.attack == MOCK_CHARIZARD_ATTACK
        assert result.defense == MOCK_CHARIZARD_DEFENSE
        assert result.special_attack == MOCK_CHARIZARD_SPECIAL_ATTACK
        assert result.special_defense == MOCK_CHARIZARD_SPECIAL_DEFENSE
        assert result.speed == MOCK_CHARIZARD_SPEED
        assert result.height == MOCK_CHARIZARD_HEIGHT
        assert result.weight == MOCK_CHARIZARD_WEIGHT
        assert result.habitat == 'mountain'

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_repository_update_commit_error(session):
        """Should raise exception when commit fails during update"""
        pokemon = Pokemon(
            name='Bulbasaur',
            order=1,
            url='https://pokeapi.co/api/v2/pokemon/1/',
            status=StatusEnum.INCOMPLETE,
            external_image='https://pokeapi.co/api/v2/pokemon/1/image.png',
        )
        session.add(pokemon)
        await session.commit()
        await session.refresh(pokemon)

        pokemon.status = StatusEnum.COMPLETE
        session.commit = AsyncMock(side_effect=Exception('Database error'))

        repository = PokemonRepository(session=session)

        with pytest.raises(Exception, match='Database error'):
            await repository.update(pokemon=pokemon)

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_repository_update_preserves_unchanged_fields(session):
        """Should preserve fields that were not changed"""
        pokemon = Pokemon(
            name='Squirtle',
            order=7,
            url='https://pokeapi.co/api/v2/pokemon/7/',
            status=StatusEnum.INCOMPLETE,
            external_image='https://pokeapi.co/api/v2/pokemon/7/image.png',
        )
        session.add(pokemon)
        await session.commit()
        await session.refresh(pokemon)

        original_name = pokemon.name
        original_order = pokemon.order
        original_url = pokemon.url

        pokemon.status = StatusEnum.COMPLETE
        pokemon.hp = MOCK_SQUIRTLE_HP

        repository = PokemonRepository(session=session)
        result = await repository.update(pokemon=pokemon)

        assert result.name == original_name
        assert result.order == original_order
        assert result.url == original_url
        assert result.status == StatusEnum.COMPLETE
        assert result.hp == MOCK_SQUIRTLE_HP
