from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.domain.pokemon.growth_rate.schema import CreatePokemonGrowthRateSchema
from app.models import PokemonGrowthRate

Session = Annotated[AsyncSession, Depends(get_session)]


class PokemonGrowthRateRepository:
    def __init__(self, session: Session):
        self.session = session

    async def create(
        self, pokemon_growth_rate: CreatePokemonGrowthRateSchema
    ) -> PokemonGrowthRate:
        growth_rate = PokemonGrowthRate(
            url=pokemon_growth_rate.url,
            name=pokemon_growth_rate.name,
            order=pokemon_growth_rate.order,
            formula=pokemon_growth_rate.formula,
        )
        self.session.add(growth_rate)
        await self.session.commit()
        await self.session.refresh(growth_rate)
        return growth_rate

    async def find_one_by_order(self, order: int) -> PokemonGrowthRate:
        return await self.session.scalar(
            select(PokemonGrowthRate).where(PokemonGrowthRate.order == order)
        )
