from http import HTTPStatus
from unittest.mock import patch, AsyncMock


class TestPokemonGrowthRateRouterList:
    @staticmethod
    def test_pokemon_growth_rate_router_list_success(
        client, trainer, token, pokemon_growth_rate
    ):
        with patch(
            'app.domain.growth_rate.service.PokemonGrowthRateService.list_all_cached',
            new_callable=AsyncMock,
        ) as mock_fetch:
            mock_fetch.return_value = [pokemon_growth_rate]
            response = client.get(
                '/growth-rate',
                headers={'Authorization': f'Bearer {token}'},
            )
            assert response.status_code == HTTPStatus.OK
            data = response.json()
            assert isinstance(data, list)
            assert len(data) == 1


class TestPokemonGrowthRateRouterFindOne:
    @staticmethod
    def test_pokemon_growth_rate_router_find_one_success(
        client, trainer, token, pokemon_growth_rate
    ):
        with patch(
            'app.domain.growth_rate.service.PokemonGrowthRateService.find_one_cached',
            new_callable=AsyncMock,
        ) as mock_fetch:
            mock_fetch.return_value = pokemon_growth_rate
            response = client.get(
                f'/growth-rate/{pokemon_growth_rate.id}',
                headers={'Authorization': f'Bearer {token}'},
            )
            assert response.status_code == HTTPStatus.OK
            data = response.json()
            assert isinstance(data, dict)
            assert data['name'] == pokemon_growth_rate.name
            assert data['created_at'] is not None
            assert data['updated_at'] is not None
            assert data['deleted_at'] is None
