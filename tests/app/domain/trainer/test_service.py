from datetime import datetime
from http import HTTPStatus
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.core.security import verify_password
from app.domain.pokemon.schema import FirstPokemonSchemaResult
from app.domain.trainer.model import Trainer
from app.domain.trainer.schema import CreateTrainerSchema, InitializeTrainerSchema
from app.shared.enums.gender_enum import GenderEnum
from app.shared.enums.role_enum import RoleEnum
from app.shared.enums.status_enum import StatusEnum
from tests.factories.pokemon import PokemonFactory

CAPTURE_RATE_HIGH = 80
CAPTURE_RATE_LOW = 10
POKEMON_CAPTURE_RATE = 60
POKEBALLS = 5


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

    @staticmethod
    @pytest.mark.asyncio
    async def test_trainer_create_service_handles_repository_error(trainer_service):
        """Should raise HTTPException when repository fails"""
        trainer_data = CreateTrainerSchema(
            name='Jane Doe',
            email='jane.doe@example.com',
            gender=GenderEnum.FEMALE,
            password='secret123',
            date_of_birth=datetime(1995, 5, 15),
        )

        trainer_service.find_one_by_email = AsyncMock(return_value=None)
        trainer_service.repository.save = AsyncMock(side_effect=Exception('boom'))
        trainer_service.pokemon_service.initialize = AsyncMock()

        with pytest.raises(HTTPException) as exc_info:
            await trainer_service.create(create_trainer=trainer_data)

        assert exc_info.value.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert exc_info.value.detail == 'Internal server error'


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
        trainer_service.repository.update.assert_called_once_with(entity=trainer)


class TestTrainerServiceInitialize:
    """Test scope for initialize method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_initialize_updates_capture_rate_when_lower(trainer_service, trainer):
        """Should update capture rate when trainer has lower rate"""
        trainer.status = StatusEnum.INCOMPLETE
        pokemon = PokemonFactory(capture_rate=POKEMON_CAPTURE_RATE)

        first_pokemon = FirstPokemonSchemaResult(
            pokemon=pokemon,
            pokemons=[pokemon],
        )

        trainer_service.find_one = AsyncMock(return_value=trainer)
        trainer_service.pokemon_service.first_pokemon = AsyncMock(return_value=first_pokemon)
        trainer_service.pokedex_service.initialize = AsyncMock()
        trainer_service.captured_pokemon_service.create = AsyncMock()
        trainer_service.repository.update = AsyncMock(return_value=trainer)

        initialize_schema = InitializeTrainerSchema(
            pokemon_name=pokemon.name,
            capture_rate=CAPTURE_RATE_LOW,
            pokeballs=POKEBALLS,
        )

        result = await trainer_service.initialize(
            trainer=trainer,
            initialize_trainer=initialize_schema,
        )

        assert result.status == StatusEnum.ACTIVE
        assert result.capture_rate == POKEMON_CAPTURE_RATE
        trainer_service.repository.update.assert_awaited_once()

    @staticmethod
    @pytest.mark.asyncio
    async def test_initialize_keeps_capture_rate_when_higher(trainer_service, trainer):
        """Should keep capture rate when trainer already has higher rate"""
        trainer.status = StatusEnum.INCOMPLETE
        trainer.capture_rate = CAPTURE_RATE_HIGH
        pokemon = PokemonFactory(capture_rate=POKEMON_CAPTURE_RATE)

        first_pokemon = FirstPokemonSchemaResult(
            pokemon=pokemon,
            pokemons=[pokemon],
        )

        trainer_service.find_one = AsyncMock(return_value=trainer)
        trainer_service.pokemon_service.first_pokemon = AsyncMock(return_value=first_pokemon)
        trainer_service.pokedex_service.initialize = AsyncMock()
        trainer_service.captured_pokemon_service.create = AsyncMock()
        trainer_service.repository.update = AsyncMock(return_value=trainer)

        initialize_schema = InitializeTrainerSchema(
            pokemon_name=pokemon.name,
            capture_rate=CAPTURE_RATE_HIGH,
            pokeballs=POKEBALLS,
        )

        result = await trainer_service.initialize(
            trainer=trainer,
            initialize_trainer=initialize_schema,
        )

        assert result.status == StatusEnum.ACTIVE
        assert result.capture_rate == CAPTURE_RATE_HIGH
        trainer_service.repository.update.assert_awaited_once()

    @staticmethod
    @pytest.mark.asyncio
    async def test_initialize_returns_trainer_when_active(trainer_service, trainer):
        """Should return trainer unchanged when already active"""
        trainer.status = StatusEnum.ACTIVE
        current_trainer = trainer

        trainer_service.find_one = AsyncMock(return_value=trainer)
        trainer_service.pokemon_service.first_pokemon = AsyncMock()

        initialize_schema = InitializeTrainerSchema(
            pokemon_name='bulbasaur',
            capture_rate=CAPTURE_RATE_LOW,
            pokeballs=POKEBALLS,
        )

        result = await trainer_service.initialize(
            trainer=current_trainer,
            initialize_trainer=initialize_schema,
        )

        assert result == current_trainer
        trainer_service.pokemon_service.first_pokemon.assert_not_called()
