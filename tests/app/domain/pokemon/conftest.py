import pytest_asyncio

from app.domain.pokemon.repository import PokemonRepository
from app.domain.pokemon.service import PokemonService


@pytest_asyncio.fixture
async def pokemon_repository(session):
    return PokemonRepository(session=session)


@pytest_asyncio.fixture
async def pokemon_service(session):
    return PokemonService(session=session)
