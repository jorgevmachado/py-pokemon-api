from typing import Annotated

from fastapi import Depends, Query
from fastapi_pagination import LimitOffsetParams
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_session
from app.domain.pokedex.model import Pokedex
from app.domain.pokedex.schema import CreatePokedexSchema, PokedexFilterPage
from app.shared.pagination import is_paginate, limit_paginate

Session = Annotated[AsyncSession, Depends(get_session)]


class PokedexRepository:
    def __init__(self, session: Session):
        self.session = session

    async def create(self, create_pokedex: CreatePokedexSchema) -> Pokedex:
        pokedex = Pokedex(
            hp=create_pokedex.hp,
            wins=create_pokedex.wins,
            level=create_pokedex.level,
            iv_hp=create_pokedex.iv_hp,
            ev_hp=create_pokedex.ev_hp,
            losses=create_pokedex.losses,
            max_hp=create_pokedex.max_hp,
            battles=create_pokedex.battles,
            nickname=create_pokedex.nickname,
            iv_speed=create_pokedex.iv_speed,
            ev_speed=create_pokedex.ev_speed,
            iv_attack=create_pokedex.iv_attack,
            ev_attack=create_pokedex.ev_attack,
            iv_defense=create_pokedex.iv_defense,
            ev_defense=create_pokedex.ev_defense,
            experience=create_pokedex.experience,
            iv_special_attack=create_pokedex.iv_special_attack,
            ev_special_attack=create_pokedex.ev_special_attack,
            iv_special_defense=create_pokedex.iv_special_defense,
            ev_special_defense=create_pokedex.ev_special_defense,
            discovered=create_pokedex.discovered,
            pokemon_id=create_pokedex.pokemon_id,
            trainer_id=create_pokedex.trainer_id,
        )
        if create_pokedex.discovered_at is not None:
            pokedex.discovered_at = create_pokedex.discovered_at

        self.session.add(pokedex)
        await self.session.commit()
        await self.session.refresh(pokedex)
        return pokedex

    async def find_by_trainer(
        self,
        trainer_id: str,
    ) -> set[str]:
        query = select(Pokedex.pokemon_id).where(
            Pokedex.trainer_id == trainer_id,
            Pokedex.trainer_id.isnot(None),
        )
        result = await self.session.scalars(query)
        return set(result.all())



    async def list_all(
            self,
            page_filter: Annotated[PokedexFilterPage, Query()]
    ):
        trainer_id = page_filter.trainer_id
        query = (
            select(Pokedex)
            .options(selectinload(Pokedex.pokemon))
            .order_by(Pokedex.discovered_at.desc())
            .where(Pokedex.trainer_id == trainer_id)
        )
        if page_filter.discovered is not None:
            query = query.where(Pokedex.discovered == page_filter.discovered)

        if page_filter.nickname is not None:
            query = query.where(Pokedex.nickname.ilike(f'%{page_filter.nickname}%'))

        if is_paginate(page_filter):
            params = LimitOffsetParams(
                limit=limit_paginate(page_filter.limit),
                offset=page_filter.offset,
            )
            return await paginate(self.session, query, params=params)
        pokedex = await self.session.scalars(query)
        return pokedex.all()

    async def find_by_pokemon(self, trainer_id: str, pokemon_id: str):
        query = (
            select(Pokedex)
            .options(selectinload(Pokedex.pokemon))
            .order_by(Pokedex.discovered_at.desc())
            .where(Pokedex.trainer_id == trainer_id, Pokedex.pokemon_id == pokemon_id)
        )
        return await self.session.scalar(query)