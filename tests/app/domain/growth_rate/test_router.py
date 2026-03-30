from http import HTTPStatus


class TestPokemonGrowthRateRouterList:
    @staticmethod
    def test_pokemon_growth_rate_router_list_success(
        client, trainer, token, pokemon_growth_rate
    ):
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
