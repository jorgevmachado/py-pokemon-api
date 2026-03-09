from datetime import datetime
from http import HTTPStatus
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.core.security import get_current_user
from app.domain.pokedex.route import CurrentTrainer, Service, router
from app.domain.pokedex.service import PokedexService
from app.main import app
from app.shared.status_enum import StatusEnum
from tests.factories.pokedex import PokedexFactory
from tests.factories.pokemon import PokemonFactory
from tests.factories.trainer import TrainerFactory

LIMIT = 10
OFFSET = 0


def build_trainer():
    trainer = TrainerFactory()
    trainer.id = str(uuid4())
    return trainer


def build_pokedex_response():
    now = datetime.now()

    pokemon = PokemonFactory()
    pokemon.id = str(uuid4())
    pokemon.created_at = now
    pokemon.updated_at = now
    pokemon.deleted_at = None
    pokemon.status = StatusEnum.COMPLETE

    pokedex = PokedexFactory()
    pokedex.id = str(uuid4())
    pokedex.pokemon = pokemon
    pokedex.discovered_at = now
    return pokedex


class TestPokedexRoute:
    """Test scope for pokedex routes"""

    @staticmethod
    def test_router_metadata():
        """Should expose correct prefix and tag"""
        assert router.prefix == '/pokedex'
        assert 'pokedex' in router.tags
        assert Service is not None
        assert CurrentTrainer is not None

    @staticmethod
    @pytest.mark.asyncio
    async def test_get_pokedex_route_calls_service(client, token):
        """Should call fetch_all and return 200"""
        trainer = build_trainer()
        pokedex = build_pokedex_response()

        mock_service = PokedexService(repository=None, pokemon_service=None)
        mock_service.fetch_all = AsyncMock(return_value=[pokedex])

        def override_service():
            return mock_service

        def override_user():
            return trainer

        app.dependency_overrides[PokedexService] = override_service
        app.dependency_overrides[get_current_user] = override_user

        response = client.get(
            '/pokedex/',
            params={'limit': LIMIT, 'offset': OFFSET},
            headers={'Authorization': f'Bearer {token}'},
        )

        app.dependency_overrides.clear()

        assert response.status_code == HTTPStatus.OK
        mock_service.fetch_all.assert_awaited_once()
        assert mock_service.fetch_all.await_args.kwargs['trainer_id'] == trainer.id

    @staticmethod
    @pytest.mark.asyncio
    async def test_discover_pokemon_route_calls_service(client, token):
        """Should call discover and return 200"""
        trainer = build_trainer()
        pokedex = build_pokedex_response()

        mock_service = PokedexService(repository=None, pokemon_service=None)
        mock_service.discover = AsyncMock(return_value=pokedex)

        def override_service():
            return mock_service

        def override_user():
            return trainer

        app.dependency_overrides[PokedexService] = override_service
        app.dependency_overrides[get_current_user] = override_user

        response = client.post(
            '/pokedex/discover',
            json={'pokemon_name': 'bulbasaur'},
            headers={'Authorization': f'Bearer {token}'},
        )

        app.dependency_overrides.clear()

        assert response.status_code == HTTPStatus.OK
        mock_service.discover.assert_awaited_once_with(
            trainer_id=trainer.id, pokemon_name='bulbasaur'
        )
