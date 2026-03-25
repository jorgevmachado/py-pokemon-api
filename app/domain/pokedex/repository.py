from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_session
from app.core.repository import BaseRepository
from app.models.pokedex import Pokedex
from app.models.pokemon import Pokemon

Session = Annotated[AsyncSession, Depends(get_session)]


class PokedexRepository(BaseRepository[Pokedex]):
    model = Pokedex
    default_order_by = 'discovered_at'
    relations = (
        selectinload(Pokedex.pokemon).selectinload(Pokemon.moves),
        selectinload(Pokedex.pokemon).selectinload(Pokemon.types),
        selectinload(Pokedex.pokemon).selectinload(Pokemon.growth_rate),
    )
