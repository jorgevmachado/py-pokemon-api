from typing import Annotated, Optional

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.domain.pokemon.external.schemas import (
    PokemonExternalBase,
)
from app.domain.pokemon.external.service import PokemonExternalService
from app.domain.pokemon.growth_rate.business import PokemonGrowthRateBusiness
from app.domain.pokemon.growth_rate.repository import PokemonGrowthRateRepository
from app.domain.pokemon.growth_rate.schema import CreatePokemonGrowthRateSchema
from app.models import PokemonGrowthRate
from app.shared.number import ensure_order_number

Session = Annotated[AsyncSession, Depends(get_session)]


class PokemonGrowthRateService:
    def __init__(self, session: Session):
        self.repository = PokemonGrowthRateRepository(session)
        self.external_service = PokemonExternalService()

    async def verify_pokemon_growth_rate(
        self, growth_rate: Optional[PokemonExternalBase] = None
    ) -> PokemonGrowthRate | None:
        if not growth_rate:
            return None
        try:
            url = growth_rate.url
            order = ensure_order_number(url)

            db_pokemon_growth_rate = await self.repository.find_one_by_order(order=order)
            if db_pokemon_growth_rate:
                return db_pokemon_growth_rate

            external_growth_rate_data = await (
                self.external_service.pokemon_external_growth_rate_by_order(order)
            )

            if not external_growth_rate_data:
                return None

            description = PokemonGrowthRateBusiness().ensure_description_message(
                external_growth_rate_data.descriptions
            )

            pokemon_growth_rate_data = CreatePokemonGrowthRateSchema(
                url=url,
                name=external_growth_rate_data.name,
                order=order,
                formula=external_growth_rate_data.formula,
                description=description,
            )

            return await self.repository.create(pokemon_growth_rate_data)
        except Exception as e:
            print(
                f'# => PokemonGrowthRateService => verify_pokemon_growth_rate => error => {e}'
            )
            return None
