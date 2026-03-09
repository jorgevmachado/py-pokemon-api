from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.domain.ability.model import PokemonAbility
from app.domain.ability.schema import CreatePokemonAbilitySchema

Session = Annotated[AsyncSession, Depends(get_session)]


class PokemonAbilityRepository:
    def __init__(self, session: Session):
        self.session = session

    async def create(self, pokemon_ability: CreatePokemonAbilitySchema) -> PokemonAbility:
        ability = PokemonAbility(
            name=pokemon_ability.name,
            url=pokemon_ability.url,
            order=pokemon_ability.order,
            slot=pokemon_ability.slot,
            is_hidden=pokemon_ability.is_hidden,
        )
        self.session.add(ability)
        await self.session.commit()
        await self.session.refresh(ability)
        return ability

    async def find_one_by_order(self, order: int) -> PokemonAbility:
        return await self.session.scalar(
            select(PokemonAbility).where(PokemonAbility.order == order)
        )
