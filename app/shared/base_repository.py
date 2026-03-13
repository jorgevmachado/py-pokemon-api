from typing import Annotated, Any, Generic, TypeVar

from fastapi import Depends, Query
from fastapi_pagination import LimitOffsetParams
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.shared.pagination import is_paginate, limit_paginate
from app.shared.schemas import FilterPage

ModelT = TypeVar('ModelT')
Session = Annotated[AsyncSession, Depends(get_session)]


class BaseRepository(Generic[ModelT]):
    model: type[ModelT]
    relations: tuple[Any, ...] = ()
    default_order_by: str | None = None

    def __init__(self, session: Session):
        self.session = session

    async def total(self):
        query = select(func.count()).select_from(self.model)
        value = await self.session.scalar(query)
        return int(value or 0)

    async def save(self, entity: ModelT) -> ModelT:
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def update(self, entity: ModelT) -> ModelT:
        await self.session.merge(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def list_all(self, page_filter: Annotated[FilterPage, Query()] = None):
        query = select(self.model)

        for option in self.relations:
            query = query.options(option)

        if self.default_order_by is not None:
            query = query.order_by(self.default_order_by)

        if page_filter is not None:
            raw_filters = page_filter.model_dump(exclude_none=True)

            raw_filters.pop('offset', None)
            raw_filters.pop('limit', None)

            valid_columns = set(self.model.__mapper__.columns.keys())
            filters = {
                k: v for k, v in raw_filters.items() if k in valid_columns and v is not None
            }

            if filters:
                query = query.filter_by(**filters)

        if is_paginate(page_filter):
            params = LimitOffsetParams(
                limit=limit_paginate(page_filter.limit),
                offset=page_filter.offset,
            )
            return await paginate(self.session, query, params=params)
        result = await self.session.scalars(query)
        return result.all()

    async def find_by(self, **kwargs) -> ModelT | None:
        query = select(self.model)

        has_special_filter = False
        pokemon_name = kwargs.pop('pokemon_name', None)
        if (
            pokemon_name is not None
            and hasattr(self.model, 'pokemon_id')
            and hasattr(self.model, 'pokemon')
        ):
            query = query.where(self.model.pokemon.has(name=pokemon_name))
            has_special_filter = True

        valid_columns = set(self.model.__mapper__.columns.keys())
        filters = {k: v for k, v in kwargs.items() if k in valid_columns and v is not None}

        if not filters and not has_special_filter:
            return None

        for option in self.relations:
            query = query.options(option)

        if filters:
            query = query.filter_by(**filters)

        return await self.session.scalar(query)
