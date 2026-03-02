import pytest_asyncio

from app.domain.ability.repository import PokemonAbilityRepository
from app.domain.ability.service import PokemonAbilityService


@pytest_asyncio.fixture
async def ability_repository(session):
    return PokemonAbilityRepository(session=session)


@pytest_asyncio.fixture
async def ability_service(session):
    return PokemonAbilityService(session=session)
