import pytest_asyncio

from app.domain.pokedex.repository import PokedexRepository
from app.domain.pokedex.service import PokedexService


@pytest_asyncio.fixture
async def pokedex_repository(session):
    return PokedexRepository(session=session)


@pytest_asyncio.fixture
async def pokedex_service(session):
    return PokedexService(session=session)
