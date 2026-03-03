from datetime import datetime
from http import HTTPStatus
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.core.security import verify_password
from app.domain.captured_pokemon.schema import CapturedPokemonFilterPage, CapturePokemonSchema
from app.domain.pokedex.schema import PokedexFilterPage
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

        first_pokemon = MagicMock(pokemon=pokemon, pokemons=[pokemon])
        trainer_service.pokemon_service.first_pokemon = AsyncMock(return_value=first_pokemon)
        trainer_service.pokedex_service.initialize = AsyncMock()
        trainer_service.captured_pokemon_service.create = AsyncMock()
        result = await trainer_service.create(create_trainer=trainer_data)

        assert isinstance(result, Trainer)
        assert result.name == 'John Doe'
        assert result.role == RoleEnum.USER
        assert result.status == StatusEnum.ACTIVE
        assert result.gender == GenderEnum.MALE
        assert verify_password('secret', result.password)
        trainer_service.pokedex_service.initialize.assert_called_once()
        trainer_service.captured_pokemon_service.create.assert_called_once()

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
    async def test_trainer_create_service_error_first_pokemon_missing(trainer_service):
        """Should raise HTTPException when fail first pokemon"""
        trainer_data = CreateTrainerSchema(
            name='John Doe',
            email='john.doe@example.com',
            gender=GenderEnum.MALE,
            password='secret',
            date_of_birth=datetime(2000, 1, 1),
            pokemon_name='missing',
        )

        trainer_service.pokemon_service.first_pokemon = AsyncMock(return_value=None)

        with pytest.raises(HTTPException) as exc_info:
            await trainer_service.create(create_trainer=trainer_data)

        assert exc_info.value.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert exc_info.value.detail == 'Error creating trainer'


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

    @staticmethod
    @pytest.mark.asyncio
    async def test_trainer_find_one_service_refreshes_pokedex_when_missing_entries(
        trainer_service,
        trainer,
    ):
        """Should refresh pokedex when trainer has fewer entries than total pokemon"""
        trainer.pokedex = []
        pokemons = [MagicMock(name='pokemon_1'), MagicMock(name='pokemon_2')]

        trainer_service.repository.find_one = AsyncMock(return_value=trainer)
        trainer_service.pokemon_service.total = AsyncMock(return_value=2)
        trainer_service.pokemon_service.fetch_all = AsyncMock(return_value=pokemons)
        trainer_service.pokedex_service.refresh = AsyncMock(return_value=[])

        result = await trainer_service.find_one(trainer.id, trainer)

        assert result == trainer
        trainer_service.pokedex_service.refresh.assert_awaited_once_with(
            trainer_id=trainer.id,
            pokemons=pokemons,
        )


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


class TestTrainerServiceListPokedex:
    """Test scope for list_pokedex method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_trainer_list_pokedex_returns_entries(trainer_service, trainer):
        """Should return paged pokedex entries when trainer has permission"""
        page_filter = PokedexFilterPage(trainer_id='placeholder')
        expected_result = ['pokedex_entry']

        trainer_service.find_one = AsyncMock(return_value=trainer)
        trainer_service.pokedex_service.fetch_all = AsyncMock(return_value=expected_result)

        result = await trainer_service.list_pokedex(
            trainer_id=trainer.id,
            current_trainer=trainer,
            page_filter=page_filter,
        )

        assert result == expected_result
        assert page_filter.trainer_id == trainer.id
        trainer_service.pokedex_service.fetch_all.assert_awaited_once_with(
            page_filter=page_filter,
        )

    @staticmethod
    @pytest.mark.asyncio
    async def test_trainer_list_pokedex_returns_forbidden_when_not_owner(
        trainer_service,
        trainer,
        other_trainer,
    ):
        """Should raise forbidden when requesting another trainer pokedex"""
        page_filter = PokedexFilterPage(trainer_id='placeholder')

        with pytest.raises(HTTPException) as exc_info:
            await trainer_service.list_pokedex(
                trainer_id=other_trainer.id,
                current_trainer=trainer,
                page_filter=page_filter,
            )

        assert exc_info.value.status_code == HTTPStatus.FORBIDDEN
        assert exc_info.value.detail == 'Not enough permissions'

    @staticmethod
    @pytest.mark.asyncio
    async def test_trainer_list_pokedex_returns_not_found_when_trainer_missing(
        trainer_service,
        trainer,
    ):
        """Should raise not found when find_one raises"""
        page_filter = PokedexFilterPage(trainer_id='placeholder')
        trainer_service.find_one = AsyncMock(
            side_effect=HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='Trainer not found',
            )
        )

        with pytest.raises(HTTPException) as exc_info:
            await trainer_service.list_pokedex(
                trainer_id=trainer.id,
                current_trainer=trainer,
                page_filter=page_filter,
            )

        assert exc_info.value.status_code == HTTPStatus.NOT_FOUND
        assert exc_info.value.detail == 'Trainer not found'

    @staticmethod
    @pytest.mark.asyncio
    async def test_trainer_list_pokedex_returns_internal_error_on_unexpected_failure(
        trainer_service,
        trainer,
    ):
        """Should raise internal error when unexpected exception occurs"""
        page_filter = PokedexFilterPage(trainer_id='placeholder')
        trainer_service.find_one = AsyncMock(side_effect=Exception('boom'))

        with pytest.raises(HTTPException) as exc_info:
            await trainer_service.list_pokedex(
                trainer_id=trainer.id,
                current_trainer=trainer,
                page_filter=page_filter,
            )

        assert exc_info.value.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert exc_info.value.detail == 'Error getting trainer pokedex'


class TestTrainerServiceListCapturedPokemon:
    """Test scope for list_captured_pokemon method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_trainer_list_captured_pokemon_returns_entries(trainer_service, trainer):
        """Should return captured pokemons when trainer has permission"""
        page_filter = CapturedPokemonFilterPage(trainer_id='placeholder')
        expected_result = ['captured_entry']

        trainer_service.find_one = AsyncMock(return_value=trainer)
        trainer_service.captured_pokemon_service.fetch_all = AsyncMock(
            return_value=expected_result
        )

        result = await trainer_service.list_captured_pokemon(
            trainer_id=trainer.id,
            current_trainer=trainer,
            page_filter=page_filter,
        )

        assert result == expected_result
        assert page_filter.trainer_id == trainer.id
        trainer_service.captured_pokemon_service.fetch_all.assert_awaited_once_with(
            page_filter=page_filter,
        )

    @staticmethod
    @pytest.mark.asyncio
    async def test_trainer_list_captured_pokemon_returns_forbidden_when_not_owner(
        trainer_service,
        trainer,
        other_trainer,
    ):
        """Should raise forbidden when requesting another trainer captured pokemons"""
        page_filter = CapturedPokemonFilterPage(trainer_id='placeholder')

        with pytest.raises(HTTPException) as exc_info:
            await trainer_service.list_captured_pokemon(
                trainer_id=other_trainer.id,
                current_trainer=trainer,
                page_filter=page_filter,
            )

        assert exc_info.value.status_code == HTTPStatus.FORBIDDEN
        assert exc_info.value.detail == 'Not enough permissions'

    @staticmethod
    @pytest.mark.asyncio
    async def test_trainer_list_captured_pokemon_returns_not_found_when_trainer_missing(
        trainer_service,
        trainer,
    ):
        """Should raise not found when find_one raises"""
        page_filter = CapturedPokemonFilterPage(trainer_id='placeholder')
        trainer_service.find_one = AsyncMock(
            side_effect=HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='Trainer not found',
            )
        )

        with pytest.raises(HTTPException) as exc_info:
            await trainer_service.list_captured_pokemon(
                trainer_id=trainer.id,
                current_trainer=trainer,
                page_filter=page_filter,
            )

        assert exc_info.value.status_code == HTTPStatus.NOT_FOUND
        assert exc_info.value.detail == 'Trainer not found'

    @staticmethod
    @pytest.mark.asyncio
    async def test_trainer_list_captured_pokemon_returns_internal_error_on_unexpected_failure(
        trainer_service,
        trainer,
    ):
        """Should raise internal error when unexpected exception occurs"""
        page_filter = CapturedPokemonFilterPage(trainer_id='placeholder')
        trainer_service.find_one = AsyncMock(side_effect=Exception('boom'))

        with pytest.raises(HTTPException) as exc_info:
            await trainer_service.list_captured_pokemon(
                trainer_id=trainer.id,
                current_trainer=trainer,
                page_filter=page_filter,
            )

        assert exc_info.value.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert exc_info.value.detail == 'Error getting trainer pokemons'


class TestTrainerServiceCapturePokemon:
    """Test scope for capture_pokemon method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_trainer_capture_pokemon_returns_entry(trainer_service, trainer, pokemon):
        """Should capture pokemon when trainer has permission"""
        capture_payload = CapturePokemonSchema(pokemon_name=pokemon.name)
        expected_result = {'captured': True}

        trainer_service.find_one = AsyncMock(return_value=trainer)
        trainer_service.pokemon_service.fetch_one = AsyncMock(return_value=pokemon)
        trainer_service.captured_pokemon_service.capture = AsyncMock(
            return_value=expected_result
        )

        result = await trainer_service.capture_pokemon(
            trainer_id=trainer.id,
            current_trainer=trainer,
            capture_pokemon=capture_payload,
        )

        assert result == expected_result
        trainer_service.pokemon_service.fetch_one.assert_awaited_once_with(name=pokemon.name)
        trainer_service.captured_pokemon_service.capture.assert_awaited_once_with(
            trainer=trainer,
            capture_pokemon=pokemon,
        )

    @staticmethod
    @pytest.mark.asyncio
    async def test_trainer_capture_pokemon_returns_forbidden_when_not_owner(
        trainer_service,
        trainer,
        other_trainer,
    ):
        """Should raise forbidden when trying to capture for another trainer"""
        capture_payload = CapturePokemonSchema(pokemon_name='pikachu')

        with pytest.raises(HTTPException) as exc_info:
            await trainer_service.capture_pokemon(
                trainer_id=other_trainer.id,
                current_trainer=trainer,
                capture_pokemon=capture_payload,
            )

        assert exc_info.value.status_code == HTTPStatus.FORBIDDEN
        assert exc_info.value.detail == 'Not enough permissions'

    @staticmethod
    @pytest.mark.asyncio
    async def test_trainer_capture_pokemon_returns_not_found_when_trainer_missing(
        trainer_service,
        trainer,
    ):
        """Should raise not found when find_one raises"""
        capture_payload = CapturePokemonSchema(pokemon_name='pikachu')
        trainer_service.find_one = AsyncMock(
            side_effect=HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='Trainer not found',
            )
        )

        with pytest.raises(HTTPException) as exc_info:
            await trainer_service.capture_pokemon(
                trainer_id=trainer.id,
                current_trainer=trainer,
                capture_pokemon=capture_payload,
            )

        assert exc_info.value.status_code == HTTPStatus.NOT_FOUND
        assert exc_info.value.detail == 'Trainer not found'

    @staticmethod
    @pytest.mark.asyncio
    async def test_trainer_capture_pokemon_returns_internal_error_on_unexpected_failure(
        trainer_service,
        trainer,
    ):
        """Should raise internal error when unexpected exception occurs"""
        capture_payload = CapturePokemonSchema(pokemon_name='pikachu')
        trainer_service.find_one = AsyncMock(side_effect=Exception('boom'))

        with pytest.raises(HTTPException) as exc_info:
            await trainer_service.capture_pokemon(
                trainer_id=trainer.id,
                current_trainer=trainer,
                capture_pokemon=capture_payload,
            )

        assert exc_info.value.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert exc_info.value.detail == 'Error trainer capture pokemon'
