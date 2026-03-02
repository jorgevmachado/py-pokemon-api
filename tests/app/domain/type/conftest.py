import pytest_asyncio

from app.domain.type.repository import PokemonTypeRepository
from app.domain.type.service import PokemonTypeService


@pytest_asyncio.fixture
async def type_repository(session):
    return PokemonTypeRepository(session=session)


@pytest_asyncio.fixture
async def type_service(session):
    return PokemonTypeService(session=session)
