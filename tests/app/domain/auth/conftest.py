import pytest_asyncio

from app.domain.auth.service import AuthService


@pytest_asyncio.fixture
async def auth_service(session):
    return AuthService(session=session)
