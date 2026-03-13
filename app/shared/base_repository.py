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

        for option in self.relations:
            query = query.options(option)

        query = query.filter_by(**kwargs)

        return await self.session.scalar(query)
