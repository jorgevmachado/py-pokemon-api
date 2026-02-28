from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from app.domain.trainer.model import Trainer
from app.domain.trainer.repository import TrainerRepository
from app.domain.trainer.schema import CreateTrainerSchema, FindOneUserSchemaParams
from app.shared.gender_enum import GenderEnum
from app.shared.role_enum import RoleEnum
from app.shared.status_enum import StatusEnum

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


class TestTrainerRepositoryCreate:
    """Test scope for create method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_trainer_repository_create_success(session):
        """Should persist trainer with default status when data is valid"""
        trainer_data = CreateTrainerSchema(
            name=MOCK_TRAINER.name,
            email=MOCK_TRAINER.email,
            gender=MOCK_TRAINER.gender,
            password=MOCK_TRAINER.password,
            date_of_birth=MOCK_TRAINER.date_of_birth,
        )

        repository = TrainerRepository(session=session)
        result = await repository.create(create_trainer=trainer_data)

        assert isinstance(result, Trainer)
        assert result.name == MOCK_TRAINER.name
        assert result.role == MOCK_TRAINER.role
        assert result.status == MOCK_TRAINER.status
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
    async def test_trainer_repository_create_success_with_optional_fields(session):
        """Should persist trainer with optional fields when data is valid"""
        trainer_data = CreateTrainerSchema(
            name=MOCK_TRAINER.name,
            email=MOCK_TRAINER.email,
            gender=MOCK_TRAINER.gender,
            password=MOCK_TRAINER.password,
            pokeballs=MOCK_POKEBALLS,
            capture_rate=MOCK_CAPTURE_RATE,
            date_of_birth=MOCK_TRAINER.date_of_birth,
        )

        repository = TrainerRepository(session=session)
        result = await repository.create(create_trainer=trainer_data)

        assert isinstance(result, Trainer)
        assert result.name == MOCK_TRAINER.name
        assert result.role == MOCK_TRAINER.role
        assert result.status == MOCK_TRAINER.status
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
    async def test_trainer_repository_create_error(session):
        """Should raise exception when commit fails"""
        trainer_data = CreateTrainerSchema(
            name=MOCK_TRAINER.name,
            email=MOCK_TRAINER.email,
            gender=MOCK_TRAINER.gender,
            password=MOCK_TRAINER.password,
            date_of_birth=MOCK_TRAINER.date_of_birth,
        )
        session.commit = AsyncMock(side_effect=Exception('Database error'))
        repository = TrainerRepository(session=session)
        with pytest.raises(Exception, match='Database error'):
            await repository.create(create_trainer=trainer_data)


class TestTrainerRepositoryUpdate:
    """Test scope for update method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_trainer_repository_update_success(session, trainer):
        """Should update trainer successfully when data is valid"""
        trainer.status = StatusEnum.ACTIVE
        trainer.pokeballs = MOCK_POKEBALLS
        trainer.capture_rate = MOCK_CAPTURE_RATE
        trainer.role = RoleEnum.ADMIN

        repository = TrainerRepository(session=session)
        result = await repository.update(trainer=trainer)

        assert result.status == StatusEnum.ACTIVE
        assert result.role == RoleEnum.ADMIN
        assert result.pokeballs == MOCK_POKEBALLS
        assert result.capture_rate == MOCK_CAPTURE_RATE
        assert result.name == trainer.name
        assert not result.pokedex
        assert not result.captured_pokemons

    @staticmethod
    @pytest.mark.asyncio
    async def test_trainer_repository_update_commit_error(session, trainer):
        """Should raise exception when commit fails during update"""
        trainer.status = StatusEnum.INACTIVE
        trainer.pokeballs = MOCK_POKEBALLS
        trainer.capture_rate = MOCK_CAPTURE_RATE
        trainer.role = RoleEnum.ADMIN

        repository = TrainerRepository(session=session)
        session.commit = AsyncMock(side_effect=Exception('Database error'))

        with pytest.raises(Exception, match='Database error'):
            await repository.update(trainer=trainer)


class TestTrainerRepositoryFindOne:
    """Test scope for find one by email method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_trainer_repository_find_one_by_email_success(session, trainer):
        """Should return trainer when email is found"""

        repository = TrainerRepository(session=session)
        result = await repository.find_one(params=FindOneUserSchemaParams(email=trainer.email))

        assert result.status == StatusEnum.ACTIVE

    @staticmethod
    @pytest.mark.asyncio
    async def test_trainer_repository_find_one_by_id_success(session, trainer):
        """Should return trainer when id is found"""

        repository = TrainerRepository(session=session)
        result = await repository.find_one(params=FindOneUserSchemaParams(id=trainer.id))

        assert result is not None

    @staticmethod
    @pytest.mark.asyncio
    async def test_trainer_repository_find_one_return_none(session, trainer):
        """Should return trainer when don't receive params"""

        repository = TrainerRepository(session=session)
        result = await repository.find_one(params=FindOneUserSchemaParams(id=None, email=None))

        assert result is None
