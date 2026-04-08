from datetime import datetime
from http import HTTPStatus
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest

from app.core.security import get_current_user
from app.domain.pokedex.route import CurrentTrainer, Service, router
from app.domain.pokedex.schema import PokedexPublicSchema
from app.domain.pokedex.service import PokedexService
from app.main import app
from app.shared.enums.status_enum import StatusEnum
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
        """Should call list_all and return 200"""
        trainer = build_trainer()
        pokedex = build_pokedex_response()

        mock_service = PokedexService(repository=None, pokemon_service=None)
        mock_service.list_all = AsyncMock(return_value=[pokedex])

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
        mock_service.list_all.assert_awaited_once()
        assert mock_service.list_all.await_args.kwargs['trainer_id'] == trainer.id

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

    @staticmethod
    @pytest.mark.asyncio
    async def test_get_pokedex_route_filters_by_pokemon_type(
        *, client, token, session, pokemon, pokemon_type, pokedex
    ):
        """Should return 200 and filter pokedex items by pokemon type"""
        pokemon.types.append(pokemon_type)
        session.add(pokemon)

        await session.commit()
        await session.refresh(pokemon)

        response = client.get(
            '/pokedex/',
            params={
                'limit': LIMIT,
                'offset': OFFSET,
                'pokemon_type': 'fire',
            },
            headers={'Authorization': f'Bearer {token}'},
        )

        assert response.status_code == HTTPStatus.OK
        response_data = response.json()
        assert 'items' in response_data
        assert len(response_data['items']) >= 1

    @staticmethod
    def test_find_one_pokedex(client, trainer, token, pokedex):
        pokedex_payload = PokedexPublicSchema.model_validate(
            build_pokedex_response()
        ).model_dump(mode='json')

        with patch(
            'app.domain.pokedex.service.PokedexService.find_one_cached',
            new_callable=AsyncMock,
        ) as mock_fetch:
            mock_fetch.return_value = pokedex_payload
            response = client.get(
                f'/pokedex/{pokedex.id}',
                headers={'Authorization': f'Bearer {token}'},
            )
            assert response.status_code == HTTPStatus.OK
            data = response.json()
            assert isinstance(data, dict)
            assert data['nickname'] == pokedex_payload['nickname']
