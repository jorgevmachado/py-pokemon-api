from datetime import datetime
from http import HTTPStatus
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.core.security import get_current_user
from app.domain.captured_pokemon.route import CurrentTrainer, Service, router
from app.domain.captured_pokemon.service import CapturedPokemonService
from app.main import app
from tests.factories.captured_pokemon import CapturedPokemonFactory
from tests.factories.pokemon import PokemonFactory
from tests.factories.trainer import TrainerFactory


def override_current_user():
    return TrainerFactory()


def build_captured_response():
    pokemon = PokemonFactory()
    now = datetime.now()
    pokemon.id = str(uuid4())
    pokemon.created_at = now
    pokemon.updated_at = now
    pokemon.deleted_at = None

    captured = CapturedPokemonFactory()
    captured.id = str(uuid4())
    captured.pokemon = pokemon
    captured.moves = []
    return captured


class TestCapturedPokemonRoute:
    """Test scope for captured pokemon routes"""

    @staticmethod
    def test_router_metadata():
        """Should expose correct prefix and tag"""
        assert router.prefix == '/captured-pokemons'
        assert 'captured-pokemons' in router.tags
        assert Service is not None
        assert CurrentTrainer is not None

    @staticmethod
    @pytest.mark.asyncio
    async def test_get_captured_pokemons_route_calls_service(client, token):
        """Should call fetch_all and return 200"""
        mock_service = CapturedPokemonService(repository=None, pokemon_service=None)
        mock_service.fetch_all = AsyncMock(return_value=[])

        def override_service():
            return mock_service

        app.dependency_overrides[CapturedPokemonService] = override_service
        app.dependency_overrides[get_current_user] = override_current_user

        response = client.get(
            '/captured-pokemons/',
            params={'limit': 10, 'offset': 0},
            headers={'Authorization': f'Bearer {token}'},
        )

        app.dependency_overrides.clear()

        assert response.status_code == HTTPStatus.OK

    @staticmethod
    @pytest.mark.asyncio
    async def test_capture_route_calls_service(client, token):
        """Should call capture and return 200"""
        captured = build_captured_response()

        mock_service = CapturedPokemonService(repository=None, pokemon_service=None)
        mock_service.capture = AsyncMock(return_value=captured)

        def override_service():
            return mock_service

        app.dependency_overrides[CapturedPokemonService] = override_service
        app.dependency_overrides[get_current_user] = override_current_user

        response = client.post(
            '/captured-pokemons/capture',
            json={'pokemon_name': 'bulbasaur', 'nickname': 'bulba'},
            headers={'Authorization': f'Bearer {token}'},
        )

        app.dependency_overrides.clear()

        assert response.status_code == HTTPStatus.OK

    @staticmethod
    @pytest.mark.asyncio
    async def test_heal_route_calls_service(client, token):
        """Should call heal and return 200"""
        captured = build_captured_response()

        mock_service = CapturedPokemonService(repository=None, pokemon_service=None)
        mock_service.heal = AsyncMock(return_value=[captured])

        def override_service():
            return mock_service

        app.dependency_overrides[CapturedPokemonService] = override_service
        app.dependency_overrides[get_current_user] = override_current_user

        response = client.post(
            '/captured-pokemons/heal',
            json={'all': True, 'pokemons': []},
            headers={'Authorization': f'Bearer {token}'},
        )

        app.dependency_overrides.clear()

        assert response.status_code == HTTPStatus.OK
