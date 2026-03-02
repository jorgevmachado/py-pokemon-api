import pytest_asyncio

from app.domain.trainer.repository import TrainerRepository
from app.domain.trainer.service import TrainerService


@pytest_asyncio.fixture
async def trainer_repository(session):
    return TrainerRepository(session=session)


@pytest_asyncio.fixture
async def trainer_service(session):
    return TrainerService(session=session)
