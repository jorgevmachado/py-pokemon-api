import pytest_asyncio

from app.domain.move.repository import PokemonMoveRepository
from app.domain.move.service import PokemonMoveService


@pytest_asyncio.fixture
async def move_repository(session):
    return PokemonMoveRepository(session=session)


@pytest_asyncio.fixture
async def move_service(session):
    return PokemonMoveService(session=session)
