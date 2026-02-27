from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from app.domain.user.repository import UserRepository
from app.domain.user.schema import CreateUserSchema, FindOneUserSchemaParams
from app.models import User
from app.shared.gender_enum import GenderEnum
from app.shared.role_enum import RoleEnum
from app.shared.status_enum import StatusEnum

MOCK_USER = User(
    name='John Doe',
    role=RoleEnum.USER,
    email='jonh.doe@example.com',
    gender=GenderEnum.MALE,
    status=StatusEnum.ACTIVE,
    password='secret',
    pokeballs=5,
    capture_rate=45,
    total_authentications=0,
    authentication_success=0,
    authentication_failures=0,
    last_authentication_at=None,
    date_of_birth=datetime.now(),
)
MOCK_POKEBALLS = 1

MOCK_CAPTURE_RATE = 200


class TestUserRepositoryCreate:
    """Test scope for create method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_user_repository_create_success(session):
        """Should persist user with default status when data is valid"""
        user_data = CreateUserSchema(
            name=MOCK_USER.name,
            email=MOCK_USER.email,
            gender=MOCK_USER.gender,
            password=MOCK_USER.password,
            date_of_birth=MOCK_USER.date_of_birth,
        )

        repository = UserRepository(session=session)
        result = await repository.create(create_user=user_data)

        assert isinstance(result, User)
        assert result.name == MOCK_USER.name
        assert result.role == MOCK_USER.role
        assert result.status == MOCK_USER.status
        assert result.gender == MOCK_USER.gender
        assert result.password == MOCK_USER.password
        assert result.pokeballs == MOCK_USER.pokeballs
        assert result.capture_rate == MOCK_USER.capture_rate
        assert result.total_authentications == MOCK_USER.total_authentications
        assert result.authentication_success == MOCK_USER.authentication_success
        assert result.authentication_failures == MOCK_USER.authentication_failures
        assert result.last_authentication_at == MOCK_USER.last_authentication_at
        assert result.date_of_birth == MOCK_USER.date_of_birth

    @staticmethod
    @pytest.mark.asyncio
    async def test_user_repository_create_success_with_optional_fields(session):
        """Should persist user with optional fields when data is valid"""
        user_data = CreateUserSchema(
            name=MOCK_USER.name,
            email=MOCK_USER.email,
            gender=MOCK_USER.gender,
            password=MOCK_USER.password,
            pokeballs=MOCK_POKEBALLS,
            capture_rate=MOCK_CAPTURE_RATE,
            date_of_birth=MOCK_USER.date_of_birth,
        )

        repository = UserRepository(session=session)
        result = await repository.create(create_user=user_data)

        assert isinstance(result, User)
        assert result.name == MOCK_USER.name
        assert result.role == MOCK_USER.role
        assert result.status == MOCK_USER.status
        assert result.gender == MOCK_USER.gender
        assert result.password == MOCK_USER.password
        assert result.pokeballs == MOCK_POKEBALLS
        assert result.capture_rate == MOCK_CAPTURE_RATE
        assert result.total_authentications == MOCK_USER.total_authentications
        assert result.authentication_success == MOCK_USER.authentication_success
        assert result.authentication_failures == MOCK_USER.authentication_failures
        assert result.last_authentication_at == MOCK_USER.last_authentication_at
        assert result.date_of_birth == MOCK_USER.date_of_birth

    @staticmethod
    @pytest.mark.asyncio
    async def test_user_repository_create_error(session):
        """Should raise exception when commit fails"""
        user_data = CreateUserSchema(
            name=MOCK_USER.name,
            email=MOCK_USER.email,
            gender=MOCK_USER.gender,
            password=MOCK_USER.password,
            date_of_birth=MOCK_USER.date_of_birth,
        )
        session.commit = AsyncMock(side_effect=Exception('Database error'))
        repository = UserRepository(session=session)
        with pytest.raises(Exception, match='Database error'):
            await repository.create(create_user=user_data)


class TestUserRepositoryUpdate:
    """Test scope for update method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_user_repository_update_success(session, user):
        """Should update user successfully when data is valid"""
        user.status = StatusEnum.ACTIVE
        user.pokeballs = MOCK_POKEBALLS
        user.capture_rate = MOCK_CAPTURE_RATE
        user.role = RoleEnum.ADMIN

        repository = UserRepository(session=session)
        result = await repository.update(user=user)

        assert result.status == StatusEnum.ACTIVE
        assert result.role == RoleEnum.ADMIN
        assert result.pokeballs == MOCK_POKEBALLS
        assert result.capture_rate == MOCK_CAPTURE_RATE
        assert result.name == user.name
        assert not result.pokedex
        assert not result.captured_pokemons

    @staticmethod
    @pytest.mark.asyncio
    async def test_user_repository_update_commit_error(session, user):
        """Should raise exception when commit fails during update"""
        user.status = StatusEnum.INACTIVE
        user.pokeballs = MOCK_POKEBALLS
        user.capture_rate = MOCK_CAPTURE_RATE
        user.role = RoleEnum.ADMIN

        repository = UserRepository(session=session)
        session.commit = AsyncMock(side_effect=Exception('Database error'))

        with pytest.raises(Exception, match='Database error'):
            await repository.update(user=user)


class TestUserRepositoryFindOne:
    """Test scope for find one by email method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_user_repository_find_one_by_email_success(session, user):
        """Should return user when email is found"""

        repository = UserRepository(session=session)
        result = await repository.find_one(params=FindOneUserSchemaParams(email=user.email))

        assert result.status == StatusEnum.ACTIVE

    @staticmethod
    @pytest.mark.asyncio
    async def test_user_repository_find_one_by_id_success(session, user):
        """Should return user when id is found"""

        repository = UserRepository(session=session)
        result = await repository.find_one(params=FindOneUserSchemaParams(id=user.id))

        assert result is not None

    @staticmethod
    @pytest.mark.asyncio
    async def test_user_repository_find_one_return_none(session, user):
        """Should return user when don't receive params"""

        repository = UserRepository(session=session)
        result = await repository.find_one(params=FindOneUserSchemaParams(id=None, email=None))

        assert result is None
