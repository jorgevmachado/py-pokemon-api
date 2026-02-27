from datetime import datetime
from http import HTTPStatus
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.domain.user.schema import CreateUserSchema
from app.domain.user.service import UserService
from app.models import User
from app.shared.gender_enum import GenderEnum
from app.shared.role_enum import RoleEnum
from app.shared.status_enum import StatusEnum


class TestUserServiceCreate:
    """Test scope for create method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_user_create_service_success(session):
        """Should create user successfully when data is valid"""
        user_data = CreateUserSchema(
            name='John Doe',
            email='john.doe@example.com',
            gender=GenderEnum.MALE,
            password='secret',
            date_of_birth=datetime(2000, 1, 1),
        )

        service = UserService(session=session)

        result = await service.create(user=user_data)

        assert isinstance(result, User)
        assert result.name == 'John Doe'
        assert result.role == RoleEnum.USER
        assert result.status == StatusEnum.ACTIVE
        assert result.gender == GenderEnum.MALE
        assert result.password == 'secret'

    @staticmethod
    @pytest.mark.asyncio
    async def test_user_create_service_return_conflict_email_exists(session, user):
        """Should raise HTTPException when email already exists"""

        user_data = CreateUserSchema(
            name='Jane Doe',
            email=user.email,
            gender=GenderEnum.FEMALE,
            password='secret123',
            date_of_birth=datetime(1995, 5, 15),
        )

        service = UserService(session=session)

        with pytest.raises(HTTPException) as exc_info:
            await service.create(user=user_data)

        assert exc_info.value.status_code == HTTPStatus.CONFLICT
        assert exc_info.value.detail == 'Email already exists'


class TestUserServiceFindOne:
    """Test scope for find one method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_user_find_one_service_return_user_success_found(session, user):
        """Should return user when found"""

        service = UserService(session=session)

        result = await service.find_one(user.id, user)

        assert isinstance(result, User)

    @staticmethod
    @pytest.mark.asyncio
    async def test_user_find_one_service_return_user_not_found(session, user):
        """Should return user not found"""

        service = UserService(session=session)
        non_existent_id = str(uuid4())

        with pytest.raises(HTTPException) as exc_info:
            await service.find_one(non_existent_id, user)

        assert exc_info.value.status_code == HTTPStatus.NOT_FOUND
        assert exc_info.value.detail == 'User not found'

    @staticmethod
    @pytest.mark.asyncio
    async def test_user_find_one_service_not_permission(session, user, other_user):
        """Should return user when found"""

        service = UserService(session=session)
        with pytest.raises(HTTPException) as exc_info:
            await service.find_one(other_user.id, user)

        assert exc_info.value.status_code == HTTPStatus.FORBIDDEN
        assert exc_info.value.detail == 'Not enough permissions'
