from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_session
from app.domain.type.model import PokemonType
from app.shared.base_repository import BaseRepository

Session = Annotated[AsyncSession, Depends(get_session)]


class PokemonTypeRepository(BaseRepository[PokemonType]):
    model = PokemonType
    default_order_by = 'order'
    relations = (selectinload(PokemonType.weaknesses), selectinload(PokemonType.strengths))
