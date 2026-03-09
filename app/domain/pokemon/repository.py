from typing import Annotated

from fastapi import Depends, Query
from fastapi_pagination import LimitOffsetParams
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_session
from app.domain.pokemon.model import Pokemon
from app.domain.pokemon.schema import CreatePokemonSchema
from app.domain.type.model import PokemonType
from app.shared.pagination import is_paginate, limit_paginate
from app.shared.schemas import FilterPage
from app.shared.status_enum import StatusEnum

Session = Annotated[AsyncSession, Depends(get_session)]


class PokemonRepository:
    def __init__(self, session: Session):
        self.session = session

    async def total(self):
        return await self.session.scalar(select(func.count()).select_from(Pokemon))

    async def list_all(self, page_filter: Annotated[FilterPage, Query()] = None):
        query = (
            select(Pokemon)
            .options(
                selectinload(Pokemon.growth_rate),
                selectinload(Pokemon.moves),
                selectinload(Pokemon.types).selectinload(PokemonType.weaknesses),
                selectinload(Pokemon.types).selectinload(PokemonType.strengths),
                selectinload(Pokemon.abilities),
                selectinload(Pokemon.evolutions)
                .selectinload(Pokemon.types)
                .selectinload(PokemonType.weaknesses)
                .selectinload(PokemonType.strengths),
                selectinload(Pokemon.evolutions).selectinload(Pokemon.growth_rate),
            )
            .order_by(Pokemon.order)
        )
        if is_paginate(page_filter):
            params = LimitOffsetParams(
                limit=limit_paginate(page_filter.limit),
                offset=page_filter.offset,
            )
            return await paginate(self.session, query, params=params)
        pokemons = await self.session.scalars(query)
        return pokemons.all()

    async def find_one(self, name: str) -> Pokemon | None:
        return await self.session.scalar(
            select(Pokemon)
            .options(
                selectinload(Pokemon.growth_rate),
                selectinload(Pokemon.moves),
                selectinload(Pokemon.types).selectinload(PokemonType.weaknesses),
                selectinload(Pokemon.types).selectinload(PokemonType.strengths),
                selectinload(Pokemon.abilities),
                selectinload(Pokemon.evolutions)
                .selectinload(Pokemon.types)
                .selectinload(PokemonType.weaknesses),
                selectinload(Pokemon.evolutions)
                .selectinload(Pokemon.types)
                .selectinload(PokemonType.strengths),
                selectinload(Pokemon.evolutions).selectinload(Pokemon.growth_rate),
            )
            .where(Pokemon.name == name)
        )

    async def create(self, pokemon_data: CreatePokemonSchema) -> Pokemon:
        pokemon = Pokemon(
            name=pokemon_data.name,
            order=pokemon_data.order,
            url=pokemon_data.url,
            status=StatusEnum.INCOMPLETE,
            external_image=pokemon_data.external_image,
        )
        self.session.add(pokemon)
        await self.session.commit()
        await self.session.refresh(pokemon)
        return pokemon

    async def update(self, pokemon: Pokemon) -> Pokemon:
        await self.session.merge(pokemon)
        await self.session.commit()
        await self.session.refresh(pokemon)
        return pokemon
