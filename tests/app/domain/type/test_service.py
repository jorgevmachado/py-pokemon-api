from unittest.mock import AsyncMock, call

import pytest

from app.domain.pokemon.external.schemas import (
    PokemonExternalBase,
    PokemonExternalBaseTypeSchemaResponse,
)
from app.models.pokemon_type import PokemonType


class TestPokemonTypeServiceSave:
    """Test scope for save method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_type_service_save_return_none(pokemon_type_service):
        order = 12
        create = PokemonExternalBase(
            url=f'https://pokeapi.co/api/v2/type/{order}/',
            name='fire',
        )
        pokemon_type_service.repository.find_by = AsyncMock(return_value=None)
        pokemon_type_service.repository.save = AsyncMock(return_value=None)
        pokemon_type_service.external_service.pokemon_external_type = AsyncMock(
            return_value=None
        )
        result = await pokemon_type_service.save(create=create)
        assert result is None
        pokemon_type_service.repository.find_by.assert_called_once()
        pokemon_type_service.repository.find_by.assert_has_calls([call(order=order)])

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_type_service_save_return_pokemon_type_from_database(
        pokemon_type, pokemon_type_service
    ):
        create = PokemonExternalBase(
            url=pokemon_type.url,
            name=pokemon_type.name,
        )
        pokemon_type_service.repository.find_by = AsyncMock(return_value=pokemon_type)
        pokemon_type_service.repository.save = AsyncMock(return_value=None)
        result = await pokemon_type_service.save(create=create)
        assert isinstance(result, PokemonType)
        assert result.name == pokemon_type.name
        assert result.order == pokemon_type.order
        assert result.text_color == pokemon_type.text_color
        assert result.background_color == pokemon_type.background_color
        pokemon_type_service.repository.find_by.assert_called_once()
        pokemon_type_service.repository.find_by.assert_has_calls([
            call(order=pokemon_type.order)
        ])

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_type_service_save_return_successfully(
        pokemon_type, pokemon_type_service
    ):
        create = PokemonExternalBase(
            url=pokemon_type.url,
            name=pokemon_type.name,
        )
        pokemon_type_service.repository.find_by = AsyncMock(return_value=None)
        pokemon_type_service.repository.save = AsyncMock(return_value=pokemon_type)
        result = await pokemon_type_service.save(create=create)
        assert isinstance(result, PokemonType)
        assert result.name == pokemon_type.name
        assert result.order == pokemon_type.order
        assert result.text_color == pokemon_type.text_color
        assert result.background_color == pokemon_type.background_color
        pokemon_type_service.repository.find_by.assert_called_once()
        pokemon_type_service.repository.find_by.assert_has_calls([
            call(order=pokemon_type.order)
        ])
        pokemon_type_service.repository.save.assert_called_once()


class TestPokemonTypeServicePersistRelations:
    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_type_service_persist_relations_empty(pokemon_type_service):
        relations: list[PokemonExternalBase] = []
        pokemon_type_service.repository.save = AsyncMock(return_value=None)
        result = await pokemon_type_service.persist_relations(relations=relations)
        assert not result
        pokemon_type_service.repository.save.assert_not_called()

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_type_service_persist_relations_success(
        pokemon_type, pokemon_type_service
    ):
        relation: PokemonExternalBase = PokemonExternalBase(
            url=pokemon_type.url,
            name=pokemon_type.name,
        )
        relations: list[PokemonExternalBase] = [relation]
        pokemon_type_service.save = AsyncMock(return_value=pokemon_type)
        result = await pokemon_type_service.persist_relations(relations=relations)
        assert isinstance(result, list)
        assert len(result) == len(relations)
        pokemon_type_service.save.assert_called_once()


class TestPokemonTypeServiceAddRelations:
    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_type_service_add_relations_with_relations(
        pokemon_type, pokemon_type_service
    ):
        pokemon_type_with_relations = PokemonType(
            url=pokemon_type.url,
            name=pokemon_type.name,
            order=pokemon_type.order,
            text_color=pokemon_type.text_color,
            background_color=pokemon_type.background_color,
        )
        pokemon_type_with_relations.weaknesses = [pokemon_type]
        pokemon_type_with_relations.strengths = [pokemon_type]
        result = await pokemon_type_service.add_relations(
            pokemon_type=pokemon_type_with_relations
        )
        assert result is not None

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_type_service_add_relations_return_without_relations(
        pokemon_type, pokemon_type_service
    ):

        pokemon_type_service.persist_relations = AsyncMock(return_value=None)
        pokemon_type_service.persist_relations = AsyncMock(return_value=None)
        result = await pokemon_type_service.add_relations(pokemon_type=pokemon_type)
        assert result is not None

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_type_service_add_relations_return_with_relations(
        pokemon_type, pokemon_type_service
    ):
        pokemon_type_with_relations = PokemonType(
            url=pokemon_type.url,
            name=pokemon_type.name,
            order=pokemon_type.order,
            text_color=pokemon_type.text_color,
            background_color=pokemon_type.background_color,
        )
        pokemon_type_with_relations.weaknesses = [pokemon_type]
        pokemon_type_with_relations.strengths = [pokemon_type]

        pokemon_type_service.persist_relations = AsyncMock(return_value=[pokemon_type])
        pokemon_type_service.persist_relations = AsyncMock(return_value=[pokemon_type])

        pokemon_type_service.repository.update = AsyncMock(
            return_value=pokemon_type_with_relations
        )

        result = await pokemon_type_service.add_relations(pokemon_type=pokemon_type)
        assert isinstance(result, PokemonType)
        assert result.weaknesses == [pokemon_type]
        assert result.strengths == [pokemon_type]
        pokemon_type_service.repository.update.assert_called_once()


class TestPokemonTypeServiceVerifyPokemonType:
    """Test scope for verify_pokemon_type method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_verify_pokemon_type_empty_success(pokemon_type_service):
        result = await pokemon_type_service.verify_pokemon_type(types=[])
        assert len(result) == 0

    @staticmethod
    @pytest.mark.asyncio
    async def test_verify_pokemon_type_in_database_success(pokemon_type, pokemon_type_service):
        types = [
            PokemonExternalBaseTypeSchemaResponse(
                slot=1, type=PokemonExternalBase(url=pokemon_type.url, name=pokemon_type.name)
            )
        ]
        pokemon_type_service.repository.find_by = AsyncMock(return_value=pokemon_type)
        pokemon_type_service.add_relations = AsyncMock(return_value=pokemon_type)
        result = await pokemon_type_service.verify_pokemon_type(types=types)
        assert len(result) == len(types)

    @staticmethod
    @pytest.mark.asyncio
    async def test_verify_pokemon_type_not_in_database_success(
        pokemon_type, pokemon_type_service
    ):
        types = [
            PokemonExternalBaseTypeSchemaResponse(
                slot=1, type=PokemonExternalBase(url=pokemon_type.url, name=pokemon_type.name)
            )
        ]
        pokemon_type_service.repository.find_by = AsyncMock(return_value=None)
        pokemon_type_service.repository.save = AsyncMock(return_value=pokemon_type)
        pokemon_type_service.add_relations = AsyncMock(return_value=pokemon_type)
        result = await pokemon_type_service.verify_pokemon_type(types=types)
        assert len(result) == len(types)

    @staticmethod
    @pytest.mark.asyncio
    async def test_verify_pokemon_type_exception(pokemon_type, pokemon_type_service):
        types = [
            PokemonExternalBaseTypeSchemaResponse(
                slot=1, type=PokemonExternalBase(url=pokemon_type.url, name=pokemon_type.name)
            )
        ]
        pokemon_type_service.repository.find_by = AsyncMock(
            side_effect=Exception('Database error')
        )
        result = await pokemon_type_service.verify_pokemon_type(types=types)
        assert len(result) == 0
