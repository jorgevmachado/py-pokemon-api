from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from app.models.trainer import Trainer
from app.shared.enums.gender_enum import GenderEnum
from app.shared.enums.role_enum import RoleEnum
from app.shared.enums.status_enum import StatusEnum

MOCK_TRAINER = Trainer(
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


class TestTrainerRepositorySave:
    """Test scope for create method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_trainer_repository_save_success(session, trainer_repository):
        """Should persist trainer with default status when data is valid"""
        result = await trainer_repository.save(entity=MOCK_TRAINER)

        assert isinstance(result, Trainer)
        assert result.name == MOCK_TRAINER.name
        assert result.role == MOCK_TRAINER.role
        assert result.status == StatusEnum.ACTIVE
        assert result.gender == MOCK_TRAINER.gender
        assert result.password == MOCK_TRAINER.password
        assert result.pokeballs == MOCK_TRAINER.pokeballs
        assert result.capture_rate == MOCK_TRAINER.capture_rate
        assert result.total_authentications == MOCK_TRAINER.total_authentications
        assert result.authentication_success == MOCK_TRAINER.authentication_success
        assert result.authentication_failures == MOCK_TRAINER.authentication_failures
        assert result.last_authentication_at == MOCK_TRAINER.last_authentication_at
        assert result.date_of_birth == MOCK_TRAINER.date_of_birth

    @staticmethod
    @pytest.mark.asyncio
    async def test_trainer_repository_save_success_with_optional_fields(
        session, trainer_repository
    ):
        """Should persist trainer with optional fields when data is valid"""
        trainer_data = Trainer(
            name=MOCK_TRAINER.name,
            role=MOCK_TRAINER.role,
            email=MOCK_TRAINER.email,
            gender=MOCK_TRAINER.gender,
            status=StatusEnum.ACTIVE,
            password=MOCK_TRAINER.password,
            pokeballs=MOCK_POKEBALLS,
            capture_rate=MOCK_CAPTURE_RATE,
            total_authentications=0,
            authentication_success=0,
            authentication_failures=0,
            last_authentication_at=None,
            date_of_birth=MOCK_TRAINER.date_of_birth,
        )

        result = await trainer_repository.save(entity=trainer_data)

        assert isinstance(result, Trainer)
        assert result.name == MOCK_TRAINER.name
        assert result.role == MOCK_TRAINER.role
        assert result.status == StatusEnum.ACTIVE
        assert result.gender == MOCK_TRAINER.gender
        assert result.password == MOCK_TRAINER.password
        assert result.pokeballs == MOCK_POKEBALLS
        assert result.capture_rate == MOCK_CAPTURE_RATE
        assert result.total_authentications == MOCK_TRAINER.total_authentications
        assert result.authentication_success == MOCK_TRAINER.authentication_success
        assert result.authentication_failures == MOCK_TRAINER.authentication_failures
        assert result.last_authentication_at == MOCK_TRAINER.last_authentication_at
        assert result.date_of_birth == MOCK_TRAINER.date_of_birth

    @staticmethod
    @pytest.mark.asyncio
    async def test_trainer_repository_save_error(session, trainer_repository):
        """Should raise exception when commit fails"""
        session.commit = AsyncMock(side_effect=Exception('Database error'))
        with pytest.raises(Exception, match='Database error'):
            await trainer_repository.save(entity=MOCK_TRAINER)


class TestTrainerRepositoryUpdate:
    """Test scope for update method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_trainer_repository_update_success(session, trainer, trainer_repository):
        """Should update trainer successfully when data is valid"""
        trainer.status = StatusEnum.ACTIVE
        trainer.pokeballs = MOCK_POKEBALLS
        trainer.capture_rate = MOCK_CAPTURE_RATE
        trainer.role = RoleEnum.ADMIN

        result = await trainer_repository.update(entity=trainer)

        assert result.status == StatusEnum.ACTIVE
        assert result.role == RoleEnum.ADMIN
        assert result.pokeballs == MOCK_POKEBALLS
        assert result.capture_rate == MOCK_CAPTURE_RATE
        assert result.name == trainer.name
        assert not result.pokedex
        assert not result.captured_pokemons

    @staticmethod
    @pytest.mark.asyncio
    async def test_trainer_repository_update_commit_error(
        session, trainer, trainer_repository
    ):
        """Should raise exception when commit fails during update"""
        trainer.status = StatusEnum.INACTIVE
        trainer.pokeballs = MOCK_POKEBALLS
        trainer.capture_rate = MOCK_CAPTURE_RATE
        trainer.role = RoleEnum.ADMIN

        session.commit = AsyncMock(side_effect=Exception('Database error'))

        with pytest.raises(Exception, match='Database error'):
            await trainer_repository.update(entity=trainer)


class TestTrainerRepositoryFindOne:
    """Test scope for find one by email method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_trainer_repository_find_by_email_success(
        session, trainer, trainer_repository
    ):
        """Should return trainer when email is found"""

        result = await trainer_repository.find_by(email=trainer.email)

        assert result.status == StatusEnum.ACTIVE

    @staticmethod
    @pytest.mark.asyncio
    async def test_trainer_repository_find_by_id_success(session, trainer, trainer_repository):
        """Should return trainer when id is found"""
        result = await trainer_repository.find_by(id=trainer.id)

        assert result is not None

    @staticmethod
    @pytest.mark.asyncio
    async def test_trainer_repository_find_one_return_none(
        session, trainer, trainer_repository
    ):
        """Should return trainer when don't receive params"""

        result = await trainer_repository.find_by(id=None, email=None)

        assert result is None
