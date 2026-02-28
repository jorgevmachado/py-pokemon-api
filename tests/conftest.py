from contextlib import contextmanager
from datetime import datetime

import factory
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from testcontainers.postgres import PostgresContainer

from app.core.base import table_registry
from app.core.database import get_session
from app.core.security import get_password_hash
from app.domain.pokemon.model import Pokemon
from app.domain.trainer.model import Trainer
from app.main import app
from app.shared.gender_enum import GenderEnum
from app.shared.role_enum import RoleEnum
from app.shared.status_enum import StatusEnum


@pytest.fixture
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()


@pytest.fixture(scope='session')
def engine():
    with PostgresContainer('postgres:17', driver='psycopg') as postgres:
        _engine = create_async_engine(postgres.get_connection_url())
        yield _engine


@pytest_asyncio.fixture
async def session(engine):
    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)


@contextmanager
def _mock_db_time(*, model, time=datetime(2024, 1, 1)):
    def fake_time_handler(mapper, connection, target):
        if hasattr(target, 'created_at'):
            target.created_at = time
        if hasattr(target, 'updated_at'):
            target.updated_at = time

    event.listen(model, 'before_insert', fake_time_handler)

    yield time

    event.remove(model, 'before_insert', fake_time_handler)


@pytest.fixture
def mock_db_time():
    return _mock_db_time


@pytest_asyncio.fixture
async def trainer(session: AsyncSession):
    password = 'testtest'
    trainer = TrainerFactory(password=get_password_hash(password))
    trainer.id = 'a6770ba6-2b19-4b6e-af76-9c11ca5ad9fd'
    trainer.email = 'john@doe.com'
    session.add(trainer)
    await session.commit()
    await session.refresh(trainer)

    trainer.clean_password = password

    return trainer


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
async def other_trainer(session: AsyncSession):
    password = 'testtest'
    trainer = TrainerFactory(password=get_password_hash(password))
    session.add(trainer)
    await session.commit()
    await session.refresh(trainer)

    trainer.clean_password = password

    return trainer


@pytest.fixture
def token(client, trainer):
    response = client.post(
        '/auth/token',
        json={'email': trainer.email, 'password': trainer.clean_password},
    )
    return response.json()['access_token']


class TrainerFactory(factory.Factory):
    class Meta:
        model = Trainer

    name = factory.Faker('name')
    email = factory.Sequence(lambda n: f'test{n}@test.com')
    password = 'hashed_password'
    gender = GenderEnum.MALE
    role = RoleEnum.USER
    status = StatusEnum.ACTIVE
    date_of_birth = '1990-07-20T00:00:00'
    pokeballs = 5
    capture_rate = 45
    total_authentications = 0
    authentication_success = 0
    authentication_failures = 0


class PokemonFactory(factory.Factory):
    class Meta:
        model = Pokemon

    name = factory.Sequence(lambda n: f'pokemon_{n}')
    order = factory.Sequence(lambda n: n)
    url = factory.Sequence(lambda n: f'https://pokeapi.co/api/v2/pokemon/{n}')
    external_image = factory.Sequence(
        lambda n: f'https://raw.githubusercontent.com/PokeAPI/sprites/{n}.png'
    )
    status = StatusEnum.COMPLETE
