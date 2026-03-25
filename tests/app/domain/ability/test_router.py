from http import HTTPStatus


class TestPokemonAbilityRouterList:
    @staticmethod
    def test_pokemon_ability_router_list_success(client, trainer, token, pokemon_ability):
        response = client.get(
            '/abilities',
            headers={'Authorization': f'Bearer {token}'},
        )
        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1


class TestPokemonAbilityRouterFindOne:
    @staticmethod
    def test_pokemon_ability_router_find_one_success(client, trainer, token, pokemon_ability):
        response = client.get(
            f'/abilities/{pokemon_ability.id}',
            headers={'Authorization': f'Bearer {token}'},
        )
        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert isinstance(data, dict)
        assert data['name'] == pokemon_ability.name
