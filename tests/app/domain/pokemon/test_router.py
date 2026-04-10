from datetime import datetime
from http import HTTPStatus
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient
from fastapi_pagination import LimitOffsetParams

from app.core.database import get_session
from app.core.pagination import CustomLimitOffsetPage
from app.main import app
from app.shared.enums.status_enum import StatusEnum
from tests.app.domain.pokemon.external.mocks.business_mock import (
    MOCK_ATTRIBUTES_ATTACK,
    MOCK_ATTRIBUTES_DEFENSE,
    MOCK_ATTRIBUTES_HP,
    MOCK_ATTRIBUTES_SPEED,
)
from tests.app.domain.pokemon.mock import MOCK_ENTITY_ORDER


class TestPokemonRouterList:
    """Test scope for list_pokemons route"""

    @staticmethod
    def test_list_pokemons_success(client, trainer, token):
        """Should return pokemon list when authorized"""
        pokemons_data = [
            SimpleNamespace(
                id='mock-pokemon-id',
                name='Bulbasaur',
                order=1,
                url='https://pokeapi.co/api/v2/pokemon/1',
                external_image='https://raw.githubusercontent.com/PokeAPI/sprites/1.png',
                status=StatusEnum.COMPLETE,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                deleted_at=None,
            ),
            SimpleNamespace(
                id='mock-pokemon-id-2',
                name='Ivysaur',
                order=2,
                url='https://pokeapi.co/api/v2/pokemon/2',
                external_image='https://raw.githubusercontent.com/PokeAPI/sprites/2.png',
                status=StatusEnum.COMPLETE,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                deleted_at=None,
            ),
        ]
        total_results = 2
        with patch(
            'app.domain.pokemon.service.PokemonService.list_all_cached', new_callable=AsyncMock
        ) as mock_fetch:
            mock_fetch.return_value = CustomLimitOffsetPage.create(
                pokemons_data,
                total=total_results,
                params=LimitOffsetParams(limit=10, offset=0),
            )
            response = client.get(
                '/pokemon/?offset=0&limit=10',
                headers={'Authorization': f'Bearer {token}'},
            )
            response_data = response.json()
            results = response_data.get('items')
            assert response.status_code == HTTPStatus.OK
            assert isinstance(response_data, dict)
            assert len(results) == total_results
            assert results[0]['name'] == 'Bulbasaur'
            assert results[1]['name'] == 'Ivysaur'

    @staticmethod
    def test_list_pokemons_empty_result(client, trainer, token):
        """Should return empty results when no pokemon exists"""
        with patch(
            'app.domain.pokemon.service.PokemonService.list_all_cached', new_callable=AsyncMock
        ) as mock_fetch:
            mock_fetch.return_value = CustomLimitOffsetPage.create(
                [],
                total=0,
                params=LimitOffsetParams(limit=10, offset=0),
            )
            response = client.get(
                '/pokemon/?offset=0&limit=10',
                headers={'Authorization': f'Bearer {token}'},
            )
            response_data = response.json()
            results = response_data.get('items')
            assert response.status_code == HTTPStatus.OK
            assert results == []

    @staticmethod
    def test_list_pokemons_with_offset(client, trainer, token):
        """Should apply offset filter correctly"""
        pokemons_data = [
            SimpleNamespace(
                id='mock-pokemon-id',
                name='Pidgeot',
                order=11,
                status=StatusEnum.COMPLETE,
                url='https://pokeapi.co/api/v2/pokemon/11',
                external_image='https://raw.githubusercontent.com/PokeAPI/sprites/11.png',
                created_at=datetime.now(),
                updated_at=datetime.now(),
                deleted_at=None,
            ),
        ]

        with patch(
            'app.domain.pokemon.service.PokemonService.list_all_cached', new_callable=AsyncMock
        ) as mock_fetch:
            mock_fetch.return_value = CustomLimitOffsetPage.create(
                pokemons_data,
                total=1,
                params=LimitOffsetParams(limit=1, offset=10),
            )

            response = client.get(
                '/pokemon/?offset=10&limit=1',
                headers={'Authorization': f'Bearer {token}'},
            )
            response_data = response.json()
            results = response_data.get('items')

            assert response.status_code == HTTPStatus.OK
            assert len(results) == 1
            assert results[0]['name'] == 'Pidgeot'

    @staticmethod
    def test_list_pokemons_with_limit(client, trainer, token):
        """Should apply limit filter correctly"""
        pokemons_data = [
            SimpleNamespace(
                id='mock-pokemon-id',
                name='Pokemon1',
                status=StatusEnum.COMPLETE,
                url='https://pokeapi.co/api/v2/pokemon/1',
                external_image='https://raw.githubusercontent.com/PokeAPI/sprites/1.png',
                order=1,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                deleted_at=None,
            ),
            SimpleNamespace(
                id='mock-pokemon-id-2',
                name='Pokemon2',
                status=StatusEnum.COMPLETE,
                url='https://pokeapi.co/api/v2/pokemon/2',
                external_image='https://raw.githubusercontent.com/PokeAPI/sprites/2.png',
                order=2,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                deleted_at=None,
            ),
        ]
        total_results = 2
        with patch(
            'app.domain.pokemon.service.PokemonService.list_all_cached', new_callable=AsyncMock
        ) as mock_fetch:
            mock_fetch.return_value = CustomLimitOffsetPage.create(
                pokemons_data,
                total=total_results,
                params=LimitOffsetParams(limit=2, offset=0),
            )

            response = client.get(
                '/pokemon/?offset=0&limit=2',
                headers={'Authorization': f'Bearer {token}'},
            )

            response_data = response.json()
            results = response_data.get('items')

            assert response.status_code == HTTPStatus.OK
            total_results = 2
            assert len(results) == total_results
            assert results[0]['name'] == 'Pokemon1'
            assert results[1]['name'] == 'Pokemon2'

    @staticmethod
    def test_list_pokemons_with_offset_and_limit(client, trainer, token):
        """Should apply both offset and limit correctly"""
        pokemons_data = [
            SimpleNamespace(
                id='mock-pokemon-id',
                name='Charizard',
                status=StatusEnum.COMPLETE,
                url='https://pokeapi.co/api/v2/pokemon/6',
                external_image='https://raw.githubusercontent.com/PokeAPI/sprites/6.png',
                order=6,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                deleted_at=None,
            ),
            SimpleNamespace(
                id='mock-pokemon-id-2',
                name='Blastoise',
                status=StatusEnum.COMPLETE,
                url='https://pokeapi.co/api/v2/pokemon/9',
                external_image='https://raw.githubusercontent.com/PokeAPI/sprites/9.png',
                order=9,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                deleted_at=None,
            ),
            SimpleNamespace(
                id='mock-pokemon-id-3',
                name='Venusaur',
                status=StatusEnum.COMPLETE,
                url='https://pokeapi.co/api/v2/pokemon/3',
                external_image='https://raw.githubusercontent.com/PokeAPI/sprites/3.png',
                order=3,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                deleted_at=None,
            ),
        ]

        with patch(
            'app.domain.pokemon.service.PokemonService.list_all_cached', new_callable=AsyncMock
        ) as mock_fetch:
            mock_fetch.return_value = CustomLimitOffsetPage.create(
                [pokemons_data[0]],
                total=3,
                params=LimitOffsetParams(limit=1, offset=2),
            )

            response = client.get(
                '/pokemon/?offset=2&limit=1',
                headers={'Authorization': f'Bearer {token}'},
            )

            response_data = response.json()
            results = response_data.get('items')

            assert response.status_code == HTTPStatus.OK
            assert len(results) == 1
            assert results[0]['name'] == 'Charizard'

    @staticmethod
    def test_list_pokemons_without_authorization(client):
        """Should return 403 when trainer is not authenticated"""
        response = client.get('/pokemon/?offset=0&limit=10')

        assert response.status_code == HTTPStatus.UNAUTHORIZED

    @staticmethod
    def test_list_pokemons_with_invalid_token(client):
        """Should return 403 when token is invalid"""
        response = client.get(
            '/pokemon/?offset=0&limit=10',
            headers={'Authorization': 'Bearer invalid_token'},
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED

    @staticmethod
    def test_list_pokemons_missing_filter_params(client, trainer, token):
        """Should return non-paginated list when query params are missing"""
        pokemons_data = [
            SimpleNamespace(
                id='mock-pokemon-id',
                name='Pikachu',
                status=StatusEnum.COMPLETE,
                url='https://pokeapi.co/api/v2/pokemon/25',
                external_image='https://raw.githubusercontent.com/PokeAPI/sprites/25.png',
                order=25,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                deleted_at=None,
            ),
        ]
        with patch(
            'app.domain.pokemon.service.PokemonService.list_all_cached', new_callable=AsyncMock
        ) as mock_fetch:
            mock_fetch.return_value = pokemons_data

            response = client.get(
                '/pokemon/',
                headers={'Authorization': f'Bearer {token}'},
            )

            assert response.status_code == HTTPStatus.OK
            mock_fetch.assert_called_once()
            page_filter = mock_fetch.call_args.kwargs['page_filter']
            assert page_filter.offset is None
            assert page_filter.limit is None

            response_data = response.json()
            assert isinstance(response_data, list)
            assert response_data[0]['name'] == 'Pikachu'

    @staticmethod
    def test_list_pokemons_service_error(session, token):
        """Should return empty results when service raises exception"""

        def get_session_override():
            return session

        with TestClient(app, raise_server_exceptions=False) as test_client:
            app.dependency_overrides[get_session] = get_session_override

            with patch(
                'app.domain.pokemon.service.PokemonService.list_all_cached',
                new_callable=AsyncMock,
            ) as mock_fetch:
                mock_fetch.side_effect = Exception('Database error')

                response = test_client.get(
                    '/pokemon/?offset=0&limit=10',
                    headers={'Authorization': f'Bearer {token}'},
                )

                assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR

            app.dependency_overrides.clear()

    @staticmethod
    def test_list_pokemons_response_structure(client, trainer, token):
        """Should return response with correct structure"""
        pokemons_data = [
            SimpleNamespace(
                id='mock-pokemon-id',
                name='Pikachu',
                order=MOCK_ENTITY_ORDER,
                status=StatusEnum.COMPLETE,
                hp=35,
                attack=55,
                defense=40,
                speed=90,
                url='https://pokeapi.co/api/v2/pokemon/25',
                external_image='https://raw.githubusercontent.com/PokeAPI/sprites/25.png',
                created_at=datetime.now(),
                updated_at=datetime.now(),
                deleted_at=None,
            ),
        ]

        with patch(
            'app.domain.pokemon.service.PokemonService.list_all_cached', new_callable=AsyncMock
        ) as mock_fetch:
            mock_fetch.return_value = CustomLimitOffsetPage.create(
                pokemons_data,
                total=1,
                params=LimitOffsetParams(limit=10, offset=0),
            )

            response = client.get(
                '/pokemon/?offset=0&limit=10',
                headers={'Authorization': f'Bearer {token}'},
            )

            assert response.status_code == HTTPStatus.OK
            response_data = response.json()
            assert isinstance(response_data, dict)
            assert 'items' in response_data

    @staticmethod
    def test_list_pokemons_preserves_pokemon_attributes(client, trainer, token):
        """Should preserve all pokemon attributes in response"""
        pokemons_data = [
            SimpleNamespace(
                id='mock-pokemon-id',
                name='Dragonite',
                order=MOCK_ENTITY_ORDER,
                status=StatusEnum.COMPLETE,
                hp=MOCK_ATTRIBUTES_HP,
                attack=MOCK_ATTRIBUTES_ATTACK,
                defense=MOCK_ATTRIBUTES_DEFENSE,
                speed=MOCK_ATTRIBUTES_SPEED,
                external_image='https://raw.githubusercontent.com/PokeAPI/sprites/149.png',
                url='https://pokeapi.co/api/v2/pokemon/149',
                created_at=datetime.now(),
                updated_at=datetime.now(),
                deleted_at=None,
            ),
        ]

        with patch(
            'app.domain.pokemon.service.PokemonService.list_all_cached', new_callable=AsyncMock
        ) as mock_fetch:
            mock_fetch.return_value = CustomLimitOffsetPage.create(
                pokemons_data,
                total=1,
                params=LimitOffsetParams(limit=10, offset=0),
            )

            response = client.get(
                '/pokemon/?offset=0&limit=10',
                headers={'Authorization': f'Bearer {token}'},
            )
            response_data = response.json()
            results = response_data.get('items')

            assert response.status_code == HTTPStatus.OK
            pokemon = results[0]
            assert pokemon['name'] == 'Dragonite'
            assert pokemon['order'] == MOCK_ENTITY_ORDER
            assert pokemon['hp'] == MOCK_ATTRIBUTES_HP
            assert pokemon['attack'] == MOCK_ATTRIBUTES_ATTACK
            assert pokemon['defense'] == MOCK_ATTRIBUTES_DEFENSE
            assert pokemon['speed'] == MOCK_ATTRIBUTES_SPEED

    @staticmethod
    def test_list_pokemons_large_offset(client, trainer, token):
        """Should handle large offset values"""
        with patch(
            'app.domain.pokemon.service.PokemonService.list_all_cached', new_callable=AsyncMock
        ) as mock_fetch:
            mock_fetch.return_value = CustomLimitOffsetPage.create(
                [],
                total=0,
                params=LimitOffsetParams(limit=10, offset=1300),
            )

            response = client.get(
                '/pokemon/?offset=1300&limit=10',
                headers={'Authorization': f'Bearer {token}'},
            )
            response_data = response.json()
            results = response_data.get('items')

            assert response.status_code == HTTPStatus.OK
            assert results == []

    @staticmethod
    def test_list_pokemons_high_limit_value(client, trainer, token):
        """Should handle high limit values"""
        pokemons_data = [
            SimpleNamespace(
                id=f'mock-pokemon-id-{i}',
                name=f'Pokemon{i}',
                status=StatusEnum.COMPLETE,
                url=f'https://pokeapi.co/api/v2/pokemon/{i}',
                external_image=f'https://raw.githubusercontent.com/PokeAPI/sprites/{i}.png',
                order=i,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                deleted_at=None,
            )
            for i in range(5)
        ]
        total_results = 5
        with patch(
            'app.domain.pokemon.service.PokemonService.list_all_cached', new_callable=AsyncMock
        ) as mock_fetch:
            mock_fetch.return_value = CustomLimitOffsetPage.create(
                pokemons_data,
                total=total_results,
                params=LimitOffsetParams(limit=100, offset=0),
            )

            response = client.get(
                '/pokemon/?offset=0&limit=1000',
                headers={'Authorization': f'Bearer {token}'},
            )
            response_data = response.json()
            results = response_data.get('items')
            assert response.status_code == HTTPStatus.OK
            assert len(results) == total_results

    @staticmethod
    def test_list_pokemons_invalid_pagination(client, trainer, token):
        """Should return validation error for invalid pagination params"""
        response = client.get(
            '/pokemon/?offset=-1&limit=0',
            headers={'Authorization': f'Bearer {token}'},
        )

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


class TestPokemonRouterDetail:
    """Test scope for detail_pokemon route"""

    @staticmethod
    def test_detail_pokemon_not_found(client, trainer, token):
        """Should return 404 when pokemon is not found"""
        response = client.get(
            '/pokemon/non-existent-pokemon',
            headers={'Authorization': f'Bearer {token}'},
        )
        assert response.status_code == HTTPStatus.NOT_FOUND
        assert response.json() == {'detail': 'Pokemon not found'}

    @staticmethod
    def test_detail_pokemon_success(client, trainer, token, session, pokemon):
        """Should return pokemon detail found"""
        with patch(
            'app.domain.pokemon.service.PokemonService.fetch_one_cached',
            new_callable=AsyncMock,
        ) as mock_fetch:
            mock_fetch.return_value = pokemon
            response = client.get(
                f'/pokemon/{pokemon.name}',
                headers={'Authorization': f'Bearer {token}'},
            )
            assert response.status_code == HTTPStatus.OK
            assert response.json()['name'] == pokemon.name
