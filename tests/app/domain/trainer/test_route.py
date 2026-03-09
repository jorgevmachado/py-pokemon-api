from datetime import datetime
from http import HTTPStatus
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.core.security import get_current_user
from app.domain.trainer.service import TrainerService
from app.main import app
from app.shared.gender_enum import GenderEnum
from app.shared.role_enum import RoleEnum
from app.shared.status_enum import StatusEnum
from tests.factories.trainer import TrainerFactory

CAPTURE_RATE = 45
POKEBALLS = 5


def build_trainer_response():
    now = datetime.now()
    trainer = TrainerFactory()
    trainer.id = str(uuid4())
    trainer.role = RoleEnum.USER
    trainer.status = StatusEnum.ACTIVE
    trainer.gender = GenderEnum.MALE
    trainer.date_of_birth = datetime(1990, 7, 20)
    trainer.pokeballs = POKEBALLS
    trainer.capture_rate = CAPTURE_RATE
    trainer.total_authentications = 0
    trainer.authentication_success = 0
    trainer.authentication_failures = 0
    trainer.last_authentication_at = None
    trainer.created_at = now
    trainer.updated_at = now
    trainer.deleted_at = None
    trainer.pokedex = []
    trainer.captured_pokemons = []
    return trainer


def test_create_trainer(client, pokemon):
    pokeballs = 5
    capture_rate = 45
    response = client.post(
        '/trainers',
        json={
            'name': 'john Doe',
            'email': 'john@doe.com',
            'password': 'password1',
            'gender': 'MALE',
            'date_of_birth': '1990-07-20',
            'pokemon_name': pokemon.name,
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    trainer = response.json()
    assert trainer['name'] == 'john Doe'
    assert trainer['email'] == 'john@doe.com'
    assert trainer['gender'] == 'MALE'
    assert trainer['date_of_birth'] == '1990-07-20T00:00:00'
    assert trainer['authentication_failures'] == 0
    assert trainer['authentication_success'] == 0
    assert trainer['total_authentications'] == 0
    assert trainer['capture_rate'] == capture_rate
    assert trainer['pokedex'] is not None
    assert trainer['captured_pokemons'] is not None
    assert trainer['pokeballs'] == pokeballs
    assert trainer['role'] == 'USER'
    assert trainer['status'] == 'INCOMPLETE'


def test_create_trainer_should_return_conflict_email_exists(client, trainer):
    response = client.post(
        '/trainers',
        json={
            'name': 'john Doe',
            'email': trainer.email,
            'password': 'password1',
            'gender': 'MALE',
            'date_of_birth': '1990-07-20',
        },
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Email already exists'}


def test_get_trainer(client, trainer, token):
    response = client.get(
        f'/trainers/{trainer.id}',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data['id'] == trainer.id
    assert data['email'] == trainer.email
    assert data['name'] == trainer.name
    assert data['email'] == trainer.email
    assert data['gender'] == trainer.gender
    assert data['date_of_birth'] == '1990-07-20T00:00:00'
    assert data['authentication_failures'] == trainer.authentication_failures
    assert data['authentication_success'] == trainer.authentication_success
    assert data['total_authentications'] == trainer.total_authentications
    assert data['capture_rate'] == trainer.capture_rate
    assert data['pokedex'] == []
    assert data['captured_pokemons'] == []
    assert data['pokeballs'] == trainer.pokeballs
    assert data['role'] == trainer.role
    assert data['status'] == trainer.status


def test_get_trainer_should_return_not_permission_error(client, other_trainer, token):
    response = client.get(
        f'/trainers/{other_trainer.id}',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}


def test_get_trainer_should_return_not_found(client, token):
    response = client.get(
        '/trainers/17aafbdd-1cd5-42a1-9516-b3a55ca52e7f',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Trainer not found'}


@pytest.mark.asyncio
async def test_initialize_trainer_calls_service(client, token):
    trainer = build_trainer_response()

    mock_service = TrainerService(
        repository=None,
        pokemon_service=None,
        pokedex_service=None,
        captured_pokemon_service=None,
    )
    mock_service.initialize = AsyncMock(return_value=trainer)

    def override_service():
        return mock_service

    def override_user():
        return trainer

    app.dependency_overrides[TrainerService] = override_service
    app.dependency_overrides[get_current_user] = override_user

    response = client.post(
        '/trainers/initialize',
        json={
            'pokemon_name': 'bulbasaur',
            'pokeballs': POKEBALLS,
            'capture_rate': CAPTURE_RATE,
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    app.dependency_overrides.clear()

    assert response.status_code == HTTPStatus.OK
    mock_service.initialize.assert_awaited_once()
