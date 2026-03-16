from contextlib import contextmanager
from datetime import datetime

import pytest
import pytest_asyncio
import redis.asyncio as redis
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer

import app.core.redis as core_redis
import app.shared.cache.cache as cache_module
from app.core.base import table_registry
from app.core.database import get_session
from app.core.security import get_password_hash
from app.main import app
from tests.factories.trainer import TrainerFactory


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


@pytest.fixture(scope='session')
def redis_container():
    with RedisContainer('redis:7.4') as container:
        yield container


@pytest_asyncio.fixture
async def session(engine):
    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)


@pytest_asyncio.fixture
async def redis_client(monkeypatch, redis_container):
    client = redis.Redis(
        host=redis_container.get_container_host_ip(),
        port=int(redis_container.get_exposed_port(6379)),
        decode_responses=True,
    )

    monkeypatch.setattr(core_redis, 'redis_client', client)
    monkeypatch.setattr(cache_module, 'redis_client', client)

    await client.flushdb()

    try:
        yield client
    finally:
        await client.flushdb()
        await client.aclose()


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
    password: str = 'testtest'
    trainer = TrainerFactory(password=get_password_hash(password))
    trainer.id = 'a6770ba6-2b19-4b6e-af76-9c11ca5ad9fd'
    trainer.email = 'john@doe.com'
    session.add(trainer)
    await session.commit()
    await session.refresh(trainer)

    trainer.clean_password = password

    return trainer


@pytest_asyncio.fixture
async def other_trainer(session: AsyncSession):
    password: str = 'testtest'
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
