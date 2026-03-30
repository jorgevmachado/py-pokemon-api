from http import HTTPStatus
from unittest.mock import AsyncMock, patch


class TestPokemonTypeRouterList:
    @staticmethod
    def test_pokemon_type_router_list_success(client, trainer, token, pokemon_type):
        with patch(
            'app.domain.type.service.PokemonTypeService.list_all_cached',
            new_callable=AsyncMock,
        ) as mock_fetch:
            mock_fetch.return_value = [pokemon_type]
            response = client.get(
                '/type',
                headers={'Authorization': f'Bearer {token}'},
            )
            assert response.status_code == HTTPStatus.OK
            data = response.json()
            assert isinstance(data, list)
            assert len(data) == 1


class TestPokemonTypeRouterFindOne:
    @staticmethod
    def test_pokemon_type_router_find_one_success(client, trainer, token, pokemon_type):
        with patch(
            'app.domain.type.service.PokemonTypeService.find_one_cached',
            new_callable=AsyncMock,
        ) as mock_fetch:
            mock_fetch.return_value = pokemon_type
            response = client.get(
                f'/type/{pokemon_type.id}',
                headers={'Authorization': f'Bearer {token}'},
            )
            assert response.status_code == HTTPStatus.OK
            data = response.json()
            assert isinstance(data, dict)
            assert data['name'] == pokemon_type.name
            assert data['created_at'] is not None
            assert data['updated_at'] is not None
            assert data['deleted_at'] is None
