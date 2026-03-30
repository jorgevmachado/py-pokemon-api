from http import HTTPStatus
from unittest.mock import patch, AsyncMock


class TestPokemonMoveRouterList:
    @staticmethod
    def test_pokemon_move_router_list_success(client, trainer, token, pokemon_move):
        with patch(
            'app.domain.move.service.PokemonMoveService.list_all_cached',
            new_callable=AsyncMock,
        ) as mock_fetch:
            mock_fetch.return_value = [pokemon_move]
            response = client.get(
                '/move',
                headers={'Authorization': f'Bearer {token}'},
            )
            assert response.status_code == HTTPStatus.OK
            data = response.json()
            assert isinstance(data, list)
            assert len(data) == 1


class TestPokemonMoveRouterFindOne:
    @staticmethod
    def test_pokemon_move_router_find_one_success(client, trainer, token, pokemon_move):
        with patch(
            'app.domain.move.service.PokemonMoveService.find_one_cached',
            new_callable=AsyncMock,
        ) as mock_fetch:
            mock_fetch.return_value = pokemon_move
            response = client.get(
                f'/move/{pokemon_move.id}',
                headers={'Authorization': f'Bearer {token}'},
            )
            assert response.status_code == HTTPStatus.OK
            data = response.json()
            assert isinstance(data, dict)
            assert data['name'] == pokemon_move.name
            assert data['created_at'] is not None
            assert data['updated_at'] is not None
            assert data['deleted_at'] is None
