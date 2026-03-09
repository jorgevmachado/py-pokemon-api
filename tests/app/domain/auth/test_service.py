from datetime import datetime
from http import HTTPStatus
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from app.domain.auth.schema import Token

MOCK_EMAIL = 'john@doe.com'
MOCK_PASSWORD = 'password1'
MOCK_TOKEN = 'token-value'


class TestAuthServiceAuthenticate:
    """Test scope for authenticate method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_authenticate_returns_token_when_valid(auth_service):
        """Should return access token when credentials are valid"""
        result_token = Token(access_token=MOCK_TOKEN, token_type='bearer')
        user = MagicMock()
        user.email = MOCK_EMAIL
        user.password = 'hashed'
        user.authentication_failures = 0
        user.total_authentications = 1
        user.authentication_success = 1
        user.last_authentication_at = None

        auth_service.trainer_service.find_one_by_email = AsyncMock(return_value=user)
        auth_service.trainer_service.update = AsyncMock(return_value=user)

        with (
            patch('app.domain.auth.service.verify_password', return_value=True),
            patch('app.domain.auth.service.create_access_token', return_value=MOCK_TOKEN),
        ):
            result = await auth_service.authenticate(MOCK_EMAIL, MOCK_PASSWORD)

        assert result == result_token
        assert isinstance(user.last_authentication_at, datetime)
        auth_service.trainer_service.update.assert_called_once_with(user)

    @staticmethod
    @pytest.mark.asyncio
    async def test_authenticate_raises_when_user_not_found(auth_service):
        """Should raise HTTPException when trainer is not found"""

        auth_service.trainer_service.find_one_by_email = AsyncMock(return_value=None)

        with pytest.raises(HTTPException) as exc_info:
            await auth_service.authenticate(MOCK_EMAIL, MOCK_PASSWORD)

        assert exc_info.value.status_code == HTTPStatus.UNAUTHORIZED
        assert exc_info.value.detail == 'Incorrect email or password'

    @staticmethod
    @pytest.mark.asyncio
    async def test_authenticate_raises_when_password_invalid(auth_service):
        """Should raise HTTPException when password is invalid"""

        user = MagicMock()
        user.email = MOCK_EMAIL
        user.password = 'hashed'
        user.authentication_failures = 1
        user.total_authentications = 2
        user.authentication_success = 1
        user.last_authentication_at = None

        auth_service.trainer_service.find_one_by_email = AsyncMock(return_value=user)
        auth_service.trainer_service.update = AsyncMock(return_value=user)

        with patch('app.domain.auth.service.verify_password', return_value=False):
            with pytest.raises(HTTPException) as exc_info:
                await auth_service.authenticate(MOCK_EMAIL, MOCK_PASSWORD)

        assert exc_info.value.status_code == HTTPStatus.UNAUTHORIZED
        assert exc_info.value.detail == 'Incorrect email or password'
        auth_service.trainer_service.update.assert_called_once_with(user)

    @staticmethod
    @pytest.mark.asyncio
    async def test_authenticate_raises_when_unexpected_error(auth_service):
        """Should raise HTTPException when unexpected error occurs"""

        auth_service.trainer_service.find_one_by_email = AsyncMock(
            side_effect=Exception('boom')
        )

        with pytest.raises(HTTPException) as exc_info:
            await auth_service.authenticate(MOCK_EMAIL, MOCK_PASSWORD)

        assert exc_info.value.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert exc_info.value.detail == 'Internal server error'
