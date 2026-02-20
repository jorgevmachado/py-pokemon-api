from typing import Annotated

from fastapi import Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession, session
from sqlalchemy.orm import selectinload

from app.database import get_session
from app.models import Pokemon
from app.shared.schemas import FilterPage
from app.shared.status_enum import StatusEnum

Session = Annotated[AsyncSession, Depends(get_session)]

class PokemonRepository:
    def __init__(self, session: Session):
        self.session = session

    async def total(self):
        return await self.session.scalar(
        select(func.count()).select_from(Pokemon)
    )

    async def list(self, pokemon_filter: Annotated[FilterPage, Query()] = FilterPage()):
        query = select(Pokemon).options(
            selectinload(Pokemon.growth_rate),
            selectinload(Pokemon.moves),
            selectinload(Pokemon.types),
            selectinload(Pokemon.abilities),
            selectinload(Pokemon.evolutions),
        )
        pokemons = await self.session.scalars(
            query
            .offset(pokemon_filter.offset)
            .limit(pokemon_filter.limit)
        )
        return pokemons.all()

    async def create(self, pokemon_data: dict):
        order = pokemon_data['order']
        pokemon = Pokemon(
            name=pokemon_data['name'],
            order=order,
            url=pokemon_data['url'],
            status=StatusEnum.INCOMPLETE,
            external_image=f'/https://www.pokemon.com/static-assets/content-assets/cms2/img/pokedex/detail/{order}.png'
        )
        self.session.add(pokemon)
        await self.session.commit()

    async def find_one(self, name: str):
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
