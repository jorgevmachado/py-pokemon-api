from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.repository import BaseRepository
from app.domain.ability.model import PokemonAbility

Session = Annotated[AsyncSession, Depends(get_session)]


class PokemonAbilityRepository(BaseRepository[PokemonAbility]):
    model = PokemonAbility
    default_order_by = 'order'
