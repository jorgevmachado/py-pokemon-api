import pytest_asyncio

from app.domain.auth.service import AuthService


@pytest_asyncio.fixture
async def auth_service(trainer_service):
    return AuthService(service=trainer_service)
