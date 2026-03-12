from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_session
from app.domain.type.model import PokemonType
from app.domain.type.schema import CreatePokemonTypeSchema

Session = Annotated[AsyncSession, Depends(get_session)]


class PokemonTypeRepository:
    def __init__(self, session: Session):
        self.session = session

    async def create(self, pokemon_type: CreatePokemonTypeSchema) -> PokemonType:
        pokemon_type = PokemonType(
            name=pokemon_type.name,
            url=pokemon_type.url,
            order=pokemon_type.order,
            text_color=pokemon_type.text_color,
            background_color=pokemon_type.background_color,
        )
        self.session.add(pokemon_type)
        await self.session.commit()
        await self.session.refresh(pokemon_type)
        return pokemon_type

    async def find_one_by_order(self, order: int) -> PokemonType:
        return await self.session.scalar(
            select(PokemonType)
            .options(selectinload(PokemonType.weaknesses))
            .options(selectinload(PokemonType.strengths))
            .where(PokemonType.order == order)
        )

    async def find_one(self, name: str) -> PokemonType:
        return await self.session.scalar(
            select(PokemonType)
            .options(selectinload(PokemonType.weaknesses))
            .options(selectinload(PokemonType.strengths))
            .where(PokemonType.name == name)
        )

    async def update(self, pokemon_type: PokemonType) -> PokemonType:
        self.session.add(pokemon_type)
        await self.session.commit()
        await self.session.refresh(pokemon_type)
        return pokemon_type
