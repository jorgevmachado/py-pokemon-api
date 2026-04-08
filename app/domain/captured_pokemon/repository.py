from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_session
from app.core.repository import BaseRepository
from app.models.captured_pokemon import CapturedPokemon
from app.models.pokemon import Pokemon
from app.models.pokemon_type import PokemonType

Session = Annotated[AsyncSession, Depends(get_session)]


class CapturedPokemonRepository(BaseRepository[CapturedPokemon]):
    model = CapturedPokemon
    default_order_by = 'captured_at'
    relations = (
        selectinload(CapturedPokemon.moves),
        selectinload(CapturedPokemon.pokemon).selectinload(Pokemon.moves),
        selectinload(CapturedPokemon.pokemon)
        .selectinload(Pokemon.types)
        .selectinload(PokemonType.strengths),
        selectinload(CapturedPokemon.pokemon)
        .selectinload(Pokemon.types)
        .selectinload(PokemonType.weaknesses),
        selectinload(CapturedPokemon.pokemon).selectinload(Pokemon.evolutions),
        selectinload(CapturedPokemon.pokemon).selectinload(Pokemon.abilities),
        selectinload(CapturedPokemon.pokemon).selectinload(Pokemon.growth_rate),
    )
