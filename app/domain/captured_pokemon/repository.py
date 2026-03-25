from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_session
from app.core.repository import BaseRepository
from app.models.captured_pokemon import CapturedPokemon
from app.models.pokemon import Pokemon

Session = Annotated[AsyncSession, Depends(get_session)]


class CapturedPokemonRepository(BaseRepository[CapturedPokemon]):
    model = CapturedPokemon
    default_order_by = 'captured_at'
    relations = (
        selectinload(CapturedPokemon.pokemon).selectinload(Pokemon.moves),
        selectinload(CapturedPokemon.pokemon).selectinload(Pokemon.types),
        selectinload(CapturedPokemon.pokemon).selectinload(Pokemon.growth_rate),
    )
