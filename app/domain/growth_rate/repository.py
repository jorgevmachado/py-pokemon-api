from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.repository import BaseRepository
from app.models.pokemon_growth_rate import PokemonGrowthRate

Session = Annotated[AsyncSession, Depends(get_session)]


class PokemonGrowthRateRepository(BaseRepository[PokemonGrowthRate]):
    model = PokemonGrowthRate
    default_order_by = 'order'
