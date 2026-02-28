from datetime import datetime
from http import HTTPStatus
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from app.domain.auth.service import AuthService

MOCK_EMAIL = 'john@doe.com'
MOCK_PASSWORD = 'password1'
MOCK_TOKEN = 'token-value'


class TestAuthServiceAuthenticate:
    """Test scope for authenticate method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_authenticate_returns_token_when_valid(session):
        """Should return access token when credentials are valid"""
        service = AuthService(session=session)
        user = MagicMock()
        user.email = MOCK_EMAIL
        user.password = 'hashed'
        user.authentication_failures = 0
        user.total_authentications = 1
        user.authentication_success = 1
        user.last_authentication_at = None

        service.trainer_service.find_one_by_email = AsyncMock(return_value=user)
        service.trainer_service.update = AsyncMock(return_value=user)

        with (
            patch('app.domain.auth.service.verify_password', return_value=True),
            patch('app.domain.auth.service.create_access_token', return_value=MOCK_TOKEN),
        ):
            result = await service.authenticate(MOCK_EMAIL, MOCK_PASSWORD)

        assert result == {'access_token': MOCK_TOKEN, 'token_type': 'bearer'}
        assert isinstance(user.last_authentication_at, datetime)
        service.trainer_service.update.assert_called_once_with(user)

    @staticmethod
    @pytest.mark.asyncio
    async def test_authenticate_raises_when_user_not_found(session):
        """Should raise HTTPException when trainer is not found"""
        service = AuthService(session=session)
        service.trainer_service.find_one_by_email = AsyncMock(return_value=None)

        with pytest.raises(HTTPException) as exc_info:
            await service.authenticate(MOCK_EMAIL, MOCK_PASSWORD)

        assert exc_info.value.status_code == HTTPStatus.UNAUTHORIZED
        assert exc_info.value.detail == 'Incorrect email or password'

    @staticmethod
    @pytest.mark.asyncio
    async def test_authenticate_raises_when_password_invalid(session):
        """Should raise HTTPException when password is invalid"""
        service = AuthService(session=session)
        user = MagicMock()
        user.email = MOCK_EMAIL
        user.password = 'hashed'
        user.authentication_failures = 1
        user.total_authentications = 2
        user.authentication_success = 1
        user.last_authentication_at = None

        service.trainer_service.find_one_by_email = AsyncMock(return_value=user)
        service.trainer_service.update = AsyncMock(return_value=user)

        with patch('app.domain.auth.service.verify_password', return_value=False):
            with pytest.raises(HTTPException) as exc_info:
                await service.authenticate(MOCK_EMAIL, MOCK_PASSWORD)

        assert exc_info.value.status_code == HTTPStatus.UNAUTHORIZED
        assert exc_info.value.detail == 'Incorrect email or password'
        service.trainer_service.update.assert_called_once_with(user)

    @staticmethod
    @pytest.mark.asyncio
    async def test_authenticate_raises_when_unexpected_error(session):
        """Should raise HTTPException when unexpected error occurs"""
        service = AuthService(session=session)
        service.trainer_service.find_one_by_email = AsyncMock(side_effect=Exception('boom'))

        with pytest.raises(HTTPException) as exc_info:
            await service.authenticate(MOCK_EMAIL, MOCK_PASSWORD)

        assert exc_info.value.status_code == HTTPStatus.UNAUTHORIZED
        assert exc_info.value.detail == 'Incorrect email or password'
