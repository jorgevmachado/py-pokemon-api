import types
from unittest.mock import AsyncMock, Mock, patch

import pytest
from sqlalchemy.orm import selectinload

from app.domain.pokedex.model import Pokedex
from app.domain.pokemon.model import Pokemon
from app.shared.base_repository import BaseRepository
from app.shared.schemas import FilterPage


class PokemonBaseRepository(BaseRepository[Pokemon]):
    model = Pokemon
    relations = (selectinload(Pokemon.moves),)
    default_order_by = 'order'


class PokedexBaseRepository(BaseRepository[Pokedex]):
    model = Pokedex


class TestBaseRepositoryTotal:
    @staticmethod
    @pytest.mark.asyncio
    async def test_total_returns_count_from_scalar():
        expected_total = 10
        mock_session = AsyncMock()
        mock_session.scalar = AsyncMock(return_value=expected_total)

        repository = PokemonBaseRepository(session=mock_session)
        result = await repository.total()

        assert result == expected_total
        mock_session.scalar.assert_awaited_once()

    @staticmethod
    @pytest.mark.asyncio
    async def test_total_returns_zero_when_scalar_is_none():
        mock_session = AsyncMock()
        mock_session.scalar = AsyncMock(return_value=None)

        repository = PokemonBaseRepository(session=mock_session)
        result = await repository.total()

        assert result == 0
        mock_session.scalar.assert_awaited_once()


class TestBaseRepositoryPersist:
    @staticmethod
    @pytest.mark.asyncio
    async def test_save_adds_commits_and_refreshes_entity():
        entity = object()
        mock_session = AsyncMock()

        repository = PokemonBaseRepository(session=mock_session)
        result = await repository.save(entity)

        assert result is entity
        mock_session.add.assert_called_once_with(entity)
        mock_session.commit.assert_awaited_once()
        mock_session.refresh.assert_awaited_once_with(entity)

    @staticmethod
    @pytest.mark.asyncio
    async def test_update_merges_commits_and_refreshes_entity():
        entity = object()
        merged_entity = object()
        mock_session = AsyncMock()
        mock_session.merge = AsyncMock(return_value=merged_entity)

        repository = PokemonBaseRepository(session=mock_session)
        result = await repository.update(entity)

        assert result is entity
        mock_session.merge.assert_awaited_once_with(entity)
        mock_session.commit.assert_awaited_once()
        mock_session.refresh.assert_awaited_once_with(entity)


class TestBaseRepositoryListAll:
    @staticmethod
    @pytest.mark.asyncio
    async def test_list_all_returns_all_items_when_not_paginated():
        expected_items = ['pikachu', 'charizard']
        scalars_result = Mock()
        scalars_result.all.return_value = expected_items

        mock_session = AsyncMock()
        mock_session.scalars = AsyncMock(return_value=scalars_result)

        repository = PokemonBaseRepository(session=mock_session)

        with patch('app.shared.base_repository.is_paginate', return_value=False):
            result = await repository.list_all()

        assert result == expected_items
        mock_session.scalars.assert_awaited_once()

    @staticmethod
    @pytest.mark.asyncio
    async def test_list_all_uses_paginate_when_page_filter_is_valid():
        result_limit = 25
        expected_page = {'items': ['pikachu'], 'total': 1}
        mock_session = AsyncMock()
        repository = PokemonBaseRepository(session=mock_session)
        page_filter = FilterPage(offset=0, limit=50)

        with (
            patch('app.shared.base_repository.is_paginate', return_value=True),
            patch('app.shared.base_repository.limit_paginate', return_value=25),
            patch(
                'app.shared.base_repository.paginate', new_callable=AsyncMock
            ) as paginate_mock,
        ):
            paginate_mock.return_value = expected_page
            result = await repository.list_all(page_filter=page_filter)

        assert result == expected_page
        mock_session.scalars.assert_not_called()
        paginate_mock.assert_awaited_once()

        called_session, called_query = paginate_mock.call_args.args[:2]
        called_params = paginate_mock.call_args.kwargs['params']

        assert called_session is mock_session
        assert called_query is not None
        assert called_params.limit == result_limit
        assert called_params.offset == 0

    @staticmethod
    @pytest.mark.asyncio
    async def test_list_all_applies_filter_by_from_page_filter():
        expected_items = ['pikachu']
        scalars_result = Mock()
        scalars_result.all.return_value = expected_items

        mock_session = AsyncMock()
        mock_session.scalars = AsyncMock(return_value=scalars_result)

        repository = PokemonBaseRepository(session=mock_session)

        with patch('app.shared.base_repository.is_paginate', return_value=False):
            result = await repository.list_all(page_filter=FilterPage.build(name='pikachu'))

        query = mock_session.scalars.await_args.args[0]

        assert result == expected_items
        assert 'pokemon.name' in str(query)


class TestBaseRepositoryFindBy:
    @staticmethod
    @pytest.mark.asyncio
    async def test_find_by_calls_filter_by_with_kwargs_and_returns_scalar_result():
        expected_entity = types.SimpleNamespace(name='pikachu')
        mock_session = AsyncMock()
        mock_session.scalar = AsyncMock(return_value=expected_entity)

        repository = PokemonBaseRepository(session=mock_session)
        result = await repository.find_by(name='pikachu', order=25)

        assert result == expected_entity
        mock_session.scalar.assert_awaited_once()

    @staticmethod
    @pytest.mark.asyncio
    async def test_find_by_returns_none_when_no_valid_filters_are_provided():
        mock_session = AsyncMock()
        repository = PokemonBaseRepository(session=mock_session)

        result = await repository.find_by(name=None, order=None)

        assert result is None
        mock_session.scalar.assert_not_called()

    @staticmethod
    @pytest.mark.asyncio
    async def test_find_by_aply_special_pokemon_name_filter_when_model_has_pokemon_relation():
        expected_entity = types.SimpleNamespace(id='pokedex-id')
        mock_session = AsyncMock()
        mock_session.scalar = AsyncMock(return_value=expected_entity)

        repository = PokedexBaseRepository(session=mock_session)

        result = await repository.find_by(trainer_id='trainer-id', pokemon_name='pikachu')
        query = mock_session.scalar.await_args.args[0]

        assert result == expected_entity
        assert 'pokemon.name' in str(query)
        assert 'pokedex.trainer_id' in str(query)
