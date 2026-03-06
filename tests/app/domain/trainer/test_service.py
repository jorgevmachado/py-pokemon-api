from datetime import datetime
from http import HTTPStatus
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.core.security import verify_password
from app.domain.trainer.model import Trainer
from app.domain.trainer.schema import CreateTrainerSchema
from app.shared.gender_enum import GenderEnum
from app.shared.role_enum import RoleEnum
from app.shared.status_enum import StatusEnum


class TestTrainerServiceCreate:
    """Test scope for create method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_trainer_create_service_success(trainer_service, pokemon):
        """Should create trainer successfully when data is valid"""
        trainer_data = CreateTrainerSchema(
            name='John Doe',
            email='john.doe@example.com',
            gender=GenderEnum.MALE,
            password='secret',
            date_of_birth=datetime(2000, 1, 1),
        )

        trainer_service.pokemon_service.initialize = AsyncMock()
        trainer_service.captured_pokemon_service.create = AsyncMock()
        result = await trainer_service.create(create_trainer=trainer_data)

        assert isinstance(result, Trainer)
        assert result.name == 'John Doe'
        assert result.role == RoleEnum.USER
        assert result.status == StatusEnum.INCOMPLETE
        assert result.gender == GenderEnum.MALE
        assert verify_password('secret', result.password)

    @staticmethod
    @pytest.mark.asyncio
    async def test_trainer_create_service_return_conflict_email_exists(
        trainer_service, trainer
    ):
        """Should raise HTTPException when email already exists"""

        trainer_data = CreateTrainerSchema(
            name='Jane Doe',
            email=trainer.email,
            gender=GenderEnum.FEMALE,
            password='secret123',
            date_of_birth=datetime(1995, 5, 15),
        )

        with pytest.raises(HTTPException) as exc_info:
            await trainer_service.create(create_trainer=trainer_data)

        assert exc_info.value.status_code == HTTPStatus.CONFLICT
        assert exc_info.value.detail == 'Email already exists'


class TestTrainerServiceFindOne:
    """Test scope for find one method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_trainer_find_one_service_return_trainer_success_found(
        trainer_service, trainer
    ):
        """Should return trainer when found"""

        result = await trainer_service.find_one(trainer.id, trainer)

        assert isinstance(result, Trainer)

    @staticmethod
    @pytest.mark.asyncio
    async def test_trainer_find_one_service_return_trainer_not_found(trainer_service, trainer):
        """Should return trainer not found"""
        non_existent_id = str(uuid4())

        with pytest.raises(HTTPException) as exc_info:
            await trainer_service.find_one(non_existent_id, trainer)

        assert exc_info.value.status_code == HTTPStatus.NOT_FOUND
        assert exc_info.value.detail == 'Trainer not found'

    @staticmethod
    @pytest.mark.asyncio
    async def test_trainer_find_one_service_not_permission(
        trainer_service, trainer, other_trainer
    ):
        """Should return trainer when found"""

        with pytest.raises(HTTPException) as exc_info:
            await trainer_service.find_one(other_trainer.id, trainer)

        assert exc_info.value.status_code == HTTPStatus.FORBIDDEN
        assert exc_info.value.detail == 'Not enough permissions'


class TestTrainerServiceFindOneByEmail:
    """Test scope for find_one_by_email method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_trainer_find_one_by_email_returns_trainer(trainer_service, trainer):
        """Should return trainer when email exists"""
        trainer_service.repository.find_one = AsyncMock(return_value=trainer)

        result = await trainer_service.find_one_by_email(email=trainer.email)

        assert result == trainer

    @staticmethod
    @pytest.mark.asyncio
    async def test_trainer_find_one_by_email_returns_none(trainer_service):
        """Should return None when email does not exist"""
        trainer_service.repository.find_one = AsyncMock(return_value=None)

        result = await trainer_service.find_one_by_email(email='missing@example.com')

        assert result is None


class TestTrainerServiceUpdate:
    """Test scope for update method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_trainer_update_returns_trainer(trainer_service, trainer):
        """Should update and return trainer"""
        trainer_service.repository.update = AsyncMock(return_value=trainer)

        result = await trainer_service.update(trainer=trainer)

        assert result == trainer
        trainer_service.repository.update.assert_called_once_with(trainer=trainer)
