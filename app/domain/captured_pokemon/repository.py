from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_session
from app.domain.captured_pokemon.model import CapturedPokemon
from app.domain.pokemon.model import Pokemon
from app.shared.base_repository import BaseRepository

Session = Annotated[AsyncSession, Depends(get_session)]


class CapturedPokemonRepository(BaseRepository[CapturedPokemon]):
    model = CapturedPokemon
    default_order_by = 'captured_at'
    relations = (
        selectinload(CapturedPokemon.pokemon).selectinload(Pokemon.moves),
        selectinload(CapturedPokemon.pokemon).selectinload(Pokemon.types),
        selectinload(CapturedPokemon.pokemon).selectinload(Pokemon.growth_rate),
    )
