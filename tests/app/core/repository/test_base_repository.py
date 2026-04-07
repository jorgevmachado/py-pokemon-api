import types
from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi_pagination import LimitOffsetPage, LimitOffsetParams
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.repository import BaseRepository
from app.models.pokedex import Pokedex
from app.models.pokemon import Pokemon
from app.shared.schemas import FilterPage


class PokemonBaseRepository(BaseRepository[Pokemon]):
    model = Pokemon
    relations = (selectinload(Pokemon.moves),)
    default_order_by = 'order'


class PokedexBaseRepository(BaseRepository[Pokedex]):
    model = Pokedex


class TestBaseRepositoryApplyOrderBy:
    @staticmethod
    def test_apply_order_by_returns_same_query_when_order_by_is_none():
        repository = PokedexBaseRepository(session=AsyncMock())
        query = select(Pokedex)
        page_filter = FilterPage()

        result_query = repository._apply_order_by(query, page_filter)

        assert result_query is query
        assert 'ORDER BY' not in str(result_query)

    @staticmethod
    def test_apply_order_by_returns_same_query_when_order_path_is_blank():
        repository = PokemonBaseRepository(session=AsyncMock())
        query = select(Pokemon)
        page_filter = FilterPage.build(order_by='   ')

        result_query = repository._apply_order_by(query, page_filter)

        assert result_query is query
        assert 'ORDER BY' not in str(result_query)

    @staticmethod
    def test_apply_order_by_uses_default_order_by_when_page_filter_is_none():
        repository = PokemonBaseRepository(session=AsyncMock())
        query = select(Pokemon)

        result_query = repository._apply_order_by(query)

        assert 'ORDER BY pokemon."order"' in str(result_query)

    @staticmethod
    def test_apply_order_by_uses_page_filter_order_by_when_provided():
        repository = PokemonBaseRepository(session=AsyncMock())
        query = select(Pokemon)
        page_filter = FilterPage.build(order_by='name')

        result_query = repository._apply_order_by(query, page_filter)

        assert 'ORDER BY pokemon.name' in str(result_query)

    @staticmethod
    def test_apply_order_by_applies_outer_join_for_relationship_path():
        repository = PokedexBaseRepository(session=AsyncMock())
        query = select(Pokedex)
        page_filter = FilterPage.build(order_by='pokemon.order')

        result_query = repository._apply_order_by(query, page_filter)
        result_query_str = str(result_query)

        assert 'LEFT OUTER JOIN pokemon' in result_query_str
        assert 'ORDER BY pokemon."order"' in result_query_str

    @staticmethod
    def test_apply_order_by_raises_error_when_relation_is_invalid():
        repository = PokedexBaseRepository(session=AsyncMock())
        query = select(Pokedex)
        page_filter = FilterPage.build(order_by='invalid.order')

        with pytest.raises(ValueError, match='Invalid default_order_by relation'):
            repository._apply_order_by(query, page_filter)

    @staticmethod
    def test_apply_order_by_raises_error_for_collection_relationship():
        repository = PokemonBaseRepository(session=AsyncMock())
        query = select(Pokemon)
        page_filter = FilterPage.build(order_by='moves.name')

        with pytest.raises(ValueError, match='collection relationships are not supported'):
            repository._apply_order_by(query, page_filter)

    @staticmethod
    def test_apply_order_by_raises_error_when_path_token_is_not_relationship():
        repository = PokemonBaseRepository(session=AsyncMock())
        query = select(Pokemon)
        page_filter = FilterPage.build(order_by='order.name')

        with pytest.raises(ValueError, match='is not a relationship'):
            repository._apply_order_by(query, page_filter)

    @staticmethod
    def test_apply_order_by_raises_error_when_last_field_is_invalid():
        repository = PokedexBaseRepository(session=AsyncMock())
        query = select(Pokedex)
        page_filter = FilterPage.build(order_by='pokemon.invalid_field')

        with pytest.raises(ValueError, match='Invalid default_order_by field'):
            repository._apply_order_by(query, page_filter)

    @staticmethod
    def test_apply_order_by_raises_error_when_last_token_is_not_column():
        repository = PokedexBaseRepository(session=AsyncMock())
        query = select(Pokedex)
        page_filter = FilterPage.build(order_by='pokemon.moves')

        with pytest.raises(ValueError, match='last token must be a mapped column'):
            repository._apply_order_by(query, page_filter)


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

        with patch('app.core.repository.base.is_paginate', return_value=False):
            result = await repository.list_all()

        assert result == expected_items
        mock_session.scalars.assert_awaited_once()

    @staticmethod
    @pytest.mark.asyncio
    async def test_list_all_uses_paginate_when_page_filter_is_valid():
        result_limit = 50
        params = LimitOffsetParams(
            limit=1,
            offset=0,
        )
        expected_page = LimitOffsetPage.create(items=['pikachu'], total=1, params=params)
        mock_session = AsyncMock()
        repository = PokemonBaseRepository(session=mock_session)
        page_filter = FilterPage(offset=0, limit=50)

        with (
            patch('app.core.repository.base.is_paginate', return_value=True),
            patch(
                'app.core.repository.base.get_limit_offset_params',
                return_value=LimitOffsetParams(limit=50, offset=0),
            ),
            patch(
                'app.core.repository.base.paginate', new_callable=AsyncMock
            ) as paginate_mock,
        ):
            paginate_mock.return_value = expected_page
            result = await repository.list_all(page_filter=page_filter)

        assert len(result.items) == 1
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

        with patch('app.core.repository.base.is_paginate', return_value=False):
            result = await repository.list_all(page_filter=FilterPage.build(name='pikachu'))

        query = mock_session.scalars.await_args.args[0]

        assert result == expected_items
        assert 'pokemon.name' in str(query)

    @staticmethod
    @pytest.mark.asyncio
    async def test_list_all_applies_model_filter_with_relational_order_by():
        expected_items = ['pokedex-item']
        scalars_result = Mock()
        scalars_result.all.return_value = expected_items

        mock_session = AsyncMock()
        mock_session.scalars = AsyncMock(return_value=scalars_result)

        repository = PokedexBaseRepository(session=mock_session)
        repository.default_order_by = 'pokemon.order'

        with patch('app.core.repository.base.is_paginate', return_value=False):
            result = await repository.list_all(
                page_filter=FilterPage.build(trainer_id='trainer-id')
            )

        query = mock_session.scalars.await_args.args[0]

        assert result == expected_items
        assert 'pokedex.trainer_id' in str(query)
        assert 'pokemon."order"' in str(query)


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
