from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_session
from app.domain.pokemon.type.schema import CreatePokemonTypeSchema
from app.models import PokemonType

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
