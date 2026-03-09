import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.ability.repository import PokemonAbilityRepository
from app.domain.ability.service import PokemonAbilityService
from app.domain.captured_pokemon.repository import CapturedPokemonRepository
from app.domain.captured_pokemon.service import CapturedPokemonService
from app.domain.growth_rate.repository import PokemonGrowthRateRepository
from app.domain.growth_rate.service import PokemonGrowthRateService
from app.domain.move.repository import PokemonMoveRepository
from app.domain.move.service import PokemonMoveService
from app.domain.pokedex.repository import PokedexRepository
from app.domain.pokedex.service import PokedexService
from app.domain.pokemon.repository import PokemonRepository
from app.domain.pokemon.service import PokemonService
from app.domain.trainer.repository import TrainerRepository
from app.domain.trainer.service import TrainerService
from app.domain.type.repository import PokemonTypeRepository
from app.domain.type.service import PokemonTypeService
from app.shared.status_enum import StatusEnum
from tests.factories.pokedex import PokedexFactory
from tests.factories.pokemon import PokemonFactory


@pytest_asyncio.fixture
async def trainer_repository(session):
    return TrainerRepository(session=session)


@pytest_asyncio.fixture
async def pokemon_repository(session):
    return PokemonRepository(session=session)


@pytest_asyncio.fixture
async def pokemon_move_repository(session):
    return PokemonMoveRepository(session=session)


@pytest_asyncio.fixture
async def pokemon_type_repository(session):
    return PokemonTypeRepository(session=session)


@pytest_asyncio.fixture
async def pokemon_ability_repository(session):
    return PokemonAbilityRepository(session=session)


@pytest_asyncio.fixture
async def pokemon_growth_rate_repository(session):
    return PokemonGrowthRateRepository(session=session)


@pytest_asyncio.fixture
async def captured_pokemon_repository(session):
    return CapturedPokemonRepository(session=session)


@pytest_asyncio.fixture
async def pokedex_repository(session):
    return PokedexRepository(session=session)


@pytest_asyncio.fixture
async def pokemon_move_service(pokemon_move_repository):
    return PokemonMoveService(repository=pokemon_move_repository)


@pytest_asyncio.fixture
async def pokemon_type_service(pokemon_type_repository):
    return PokemonTypeService(repository=pokemon_type_repository)


@pytest_asyncio.fixture
async def pokemon_ability_service(pokemon_ability_repository):
    return PokemonAbilityService(repository=pokemon_ability_repository)


@pytest_asyncio.fixture
async def pokemon_growth_rate_service(pokemon_growth_rate_repository):
    return PokemonGrowthRateService(repository=pokemon_growth_rate_repository)


@pytest_asyncio.fixture
async def captured_pokemon_service(captured_pokemon_repository, pokemon_service):
    return CapturedPokemonService(
        repository=captured_pokemon_repository, pokemon_service=pokemon_service
    )


@pytest_asyncio.fixture
async def pokedex_service(pokedex_repository, pokemon_service):
    return PokedexService(repository=pokedex_repository, pokemon_service=pokemon_service)


@pytest_asyncio.fixture
async def pokemon_service(
    pokemon_repository,
    pokemon_move_service,
    pokemon_type_service,
    pokemon_ability_service,
    pokemon_growth_rate_service,
):
    return PokemonService(
        repository=pokemon_repository,
        pokemon_move_service=pokemon_move_service,
        pokemon_type_service=pokemon_type_service,
        pokemon_ability_service=pokemon_ability_service,
        pokemon_growth_rate_service=pokemon_growth_rate_service,
    )


@pytest_asyncio.fixture
async def trainer_service(
    pokemon_service, pokedex_service, trainer_repository, captured_pokemon_service
):
    return TrainerService(
        repository=trainer_repository,
        pokemon_service=pokemon_service,
        pokedex_service=pokedex_service,
        captured_pokemon_service=captured_pokemon_service,
    )


@pytest_asyncio.fixture
async def pokemon(session: AsyncSession):
    pokemon = PokemonFactory()
    session.add(pokemon)
    await session.commit()
    await session.refresh(pokemon)

    return pokemon


@pytest_asyncio.fixture
async def pokemon_incomplete(session: AsyncSession):
    pokemon = PokemonFactory(status=StatusEnum.INCOMPLETE)
    session.add(pokemon)
    await session.commit()
    await session.refresh(pokemon)

    return pokemon


@pytest_asyncio.fixture
async def pokedex(session: AsyncSession, pokemon, trainer):
    pokedex = PokedexFactory(pokemon_id=pokemon.id, trainer_id=trainer.id)
    session.add(pokedex)
    await session.commit()
    await session.refresh(pokedex)

    return pokedex
