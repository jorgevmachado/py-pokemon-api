from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import Type

Session = Annotated[AsyncSession, Depends(get_session)]


class PokemonTypeRepository:
    def __init__(self, session: Session):
        self.session = session

    async def create(self, type: Type):
        try:
            pokemon_type = Type(type=type)
            self.session.add(pokemon_type)
            await self.session.commit()
        except Exception as e:
            print(f'# => PokemonTypeRepository => create => error => {e}')
            return None

    async def find_one_by_order(self, order: int):
        try:
            return await self.session.scalar(
                select(Type)
                .where(Type.order == order)
            )
        except Exception as e:
            print(f'# => PokemonTypeRepository => find_one_by_order => error => {e}')
            return None

