import pytest_asyncio

from app.domain.growth_rate.repository import PokemonGrowthRateRepository
from app.domain.growth_rate.service import PokemonGrowthRateService


@pytest_asyncio.fixture
async def growth_rate_repository(session):

    return PokemonGrowthRateRepository(session=session)


@pytest_asyncio.fixture
async def growth_rate_service(session):

    return PokemonGrowthRateService(session=session)
