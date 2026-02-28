from datetime import datetime
from http import HTTPStatus
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.core.security import verify_password
from app.domain.trainer.model import Trainer
from app.domain.trainer.schema import CreateTrainerSchema, TrainerInitializeTrainerSchema
from app.domain.trainer.service import TrainerService
from app.shared.gender_enum import GenderEnum
from app.shared.role_enum import RoleEnum
from app.shared.status_enum import StatusEnum


class TestTrainerServiceCreate:
    """Test scope for create method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_trainer_create_service_success(session):
        """Should create trainer successfully when data is valid"""
        trainer_data = CreateTrainerSchema(
            name='John Doe',
            email='john.doe@example.com',
            gender=GenderEnum.MALE,
            password='secret',
            date_of_birth=datetime(2000, 1, 1),
        )

        service = TrainerService(session=session)

        result = await service.create(trainer=trainer_data)

        assert isinstance(result, Trainer)
        assert result.name == 'John Doe'
        assert result.role == RoleEnum.USER
        assert result.status == StatusEnum.ACTIVE
        assert result.gender == GenderEnum.MALE
        assert verify_password('secret', result.password)

    @staticmethod
    @pytest.mark.asyncio
    async def test_trainer_create_service_return_conflict_email_exists(session, trainer):
        """Should raise HTTPException when email already exists"""

        trainer_data = CreateTrainerSchema(
            name='Jane Doe',
            email=trainer.email,
            gender=GenderEnum.FEMALE,
            password='secret123',
            date_of_birth=datetime(1995, 5, 15),
        )

        service = TrainerService(session=session)

        with pytest.raises(HTTPException) as exc_info:
            await service.create(trainer=trainer_data)

        assert exc_info.value.status_code == HTTPStatus.CONFLICT
        assert exc_info.value.detail == 'Email already exists'


class TestTrainerServiceFindOne:
    """Test scope for find one method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_trainer_find_one_service_return_trainer_success_found(session, trainer):
        """Should return trainer when found"""

        service = TrainerService(session=session)

        result = await service.find_one(trainer.id, trainer)

        assert isinstance(result, Trainer)

    @staticmethod
    @pytest.mark.asyncio
    async def test_trainer_find_one_service_return_trainer_not_found(session, trainer):
        """Should return trainer not found"""

        service = TrainerService(session=session)
        non_existent_id = str(uuid4())

        with pytest.raises(HTTPException) as exc_info:
            await service.find_one(non_existent_id, trainer)

        assert exc_info.value.status_code == HTTPStatus.NOT_FOUND
        assert exc_info.value.detail == 'Trainer not found'

    @staticmethod
    @pytest.mark.asyncio
    async def test_trainer_find_one_service_not_permission(session, trainer, other_trainer):
        """Should return trainer when found"""

        service = TrainerService(session=session)
        with pytest.raises(HTTPException) as exc_info:
            await service.find_one(other_trainer.id, trainer)

        assert exc_info.value.status_code == HTTPStatus.FORBIDDEN
        assert exc_info.value.detail == 'Not enough permissions'


class TestTrainerServiceFindOneByEmail:
    """Test scope for find_one_by_email method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_trainer_find_one_by_email_returns_trainer(session, trainer):
        """Should return trainer when email exists"""
        service = TrainerService(session=session)
        service.repository.find_one = AsyncMock(return_value=trainer)

        result = await service.find_one_by_email(email=trainer.email)

        assert result == trainer

    @staticmethod
    @pytest.mark.asyncio
    async def test_trainer_find_one_by_email_returns_none(session):
        """Should return None when email does not exist"""
        service = TrainerService(session=session)
        service.repository.find_one = AsyncMock(return_value=None)

        result = await service.find_one_by_email(email='missing@example.com')

        assert result is None


class TestTrainerServiceUpdate:
    """Test scope for update method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_trainer_update_returns_trainer(session, trainer):
        """Should update and return trainer"""
        service = TrainerService(session=session)
        service.repository.update = AsyncMock(return_value=trainer)

        result = await service.update(trainer=trainer)

        assert result == trainer
        service.repository.update.assert_called_once_with(trainer=trainer)


class TestTrainerServiceInitialize:
    """Test scope for initialize method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_trainer_initialize_returns_trainer_when_active(session, trainer):
        """Should return trainer when status is active"""
        service = TrainerService(session=session)
        trainer.status = StatusEnum.ACTIVE
        service.find_one = AsyncMock(return_value=trainer)
        service.pokemon_service.first_pokemon = AsyncMock()

        params = TrainerInitializeTrainerSchema(pokemon_name='pikachu')
        result = await service.initialize(params=params, current_trainer=trainer)

        assert result == trainer
        service.pokemon_service.first_pokemon.assert_not_called()

    @staticmethod
    @pytest.mark.asyncio
    async def test_trainer_initialize_raises_internal_error_when_first_pokemon_missing(
        session, trainer
    ):
        """Should raise HTTPException when first pokemon is not found"""
        service = TrainerService(session=session)
        trainer.status = StatusEnum.INCOMPLETE
        trainer.pokedex = []
        trainer.captured_pokemons = []
        service.find_one = AsyncMock(return_value=trainer)
        service.pokemon_service.first_pokemon = AsyncMock(return_value=None)

        params = TrainerInitializeTrainerSchema(pokemon_name='missing')

        with pytest.raises(HTTPException) as exc_info:
            await service.initialize(params=params, current_trainer=trainer)

        assert exc_info.value.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert exc_info.value.detail == 'Error initializing trainer'

    @staticmethod
    @pytest.mark.asyncio
    async def test_trainer_initialize_sets_active_and_updates_trainer(
        session, trainer, pokemon
    ):
        """Should initialize pokedex and captured pokemon and update status"""
        service = TrainerService(session=session)
        trainer.status = StatusEnum.INCOMPLETE
        trainer.pokedex = []
        trainer.captured_pokemons = []
        service.find_one = AsyncMock(return_value=trainer)
        first_pokemon = MagicMock(pokemon=pokemon, pokemons=[pokemon])
        service.pokemon_service.first_pokemon = AsyncMock(return_value=first_pokemon)
        service.pokedex_service.initialize = AsyncMock()
        service.captured_pokemon_service.create = AsyncMock()
        service.repository.update = AsyncMock(return_value=trainer)

        params = TrainerInitializeTrainerSchema(pokemon_name='pikachu')
        result = await service.initialize(params=params, current_trainer=trainer)

        assert result == trainer
        assert trainer.status == StatusEnum.ACTIVE
        service.pokedex_service.initialize.assert_called_once()
        service.captured_pokemon_service.create.assert_called_once()
        service.repository.update.assert_called_once_with(trainer=trainer)
