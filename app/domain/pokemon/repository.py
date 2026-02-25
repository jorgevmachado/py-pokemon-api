from typing import Annotated

from fastapi import Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_session
from app.domain.pokemon.schema import CreatePokemonSchema
from app.models import Pokemon
from app.shared.schemas import FilterPage
from app.shared.status_enum import StatusEnum

Session = Annotated[AsyncSession, Depends(get_session)]


class PokemonRepository:
    def __init__(self, session: Session):
        self.session = session

    async def total(self):
        return await self.session.scalar(select(func.count()).select_from(Pokemon))

    async def list(self, pokemon_filter: Annotated[FilterPage, Query()] = FilterPage()):
        query = select(Pokemon).options(
            selectinload(Pokemon.growth_rate),
            selectinload(Pokemon.moves),
            selectinload(Pokemon.types),
            selectinload(Pokemon.abilities),
            selectinload(Pokemon.evolutions),
        )
        pokemons = await self.session.scalars(
            query.offset(pokemon_filter.offset).limit(pokemon_filter.limit)
        )
        return pokemons.all()

    async def find_one(self, name: str) -> Pokemon | None:
        return await self.session.scalar(
            select(Pokemon)
            .options(
                selectinload(Pokemon.growth_rate),
                selectinload(Pokemon.moves),
                selectinload(Pokemon.types),
                selectinload(Pokemon.abilities),
                selectinload(Pokemon.evolutions),
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
