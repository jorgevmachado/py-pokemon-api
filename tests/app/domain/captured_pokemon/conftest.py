import pytest_asyncio

from app.domain.captured_pokemon.repository import CapturedPokemonRepository
from app.domain.captured_pokemon.service import CapturedPokemonService


@pytest_asyncio.fixture
async def captured_pokemon_repository(session):
    return CapturedPokemonRepository(session=session)


@pytest_asyncio.fixture
async def captured_pokemon_service(session):
    return CapturedPokemonService(session=session)
