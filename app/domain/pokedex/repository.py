from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_session
from app.domain.pokedex.model import Pokedex
from app.domain.pokemon.model import Pokemon
from app.shared.base_repository import BaseRepository

Session = Annotated[AsyncSession, Depends(get_session)]


class PokedexRepository(BaseRepository[Pokedex]):
    model = Pokedex
    default_order_by = 'discovered_at'
    relations = (
        selectinload(Pokedex.pokemon).selectinload(Pokemon.moves),
        selectinload(Pokedex.pokemon).selectinload(Pokemon.types),
        selectinload(Pokedex.pokemon).selectinload(Pokemon.growth_rate),
    )
