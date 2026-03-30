from http import HTTPStatus
from unittest.mock import AsyncMock, patch


class TestPokemonAbilityRouterList:
    @staticmethod
    def test_pokemon_ability_router_list_success(client, trainer, token, pokemon_ability):
        with patch(
            'app.domain.ability.service.PokemonAbilityService.list_all_cached',
            new_callable=AsyncMock,
        ) as mock_fetch:
            mock_fetch.return_value = [pokemon_ability]
            response = client.get(
                '/ability',
                headers={'Authorization': f'Bearer {token}'},
            )
            assert response.status_code == HTTPStatus.OK
            data = response.json()
            assert isinstance(data, list)
            assert len(data) == 1


class TestPokemonAbilityRouterFindOne:
    @staticmethod
    def test_pokemon_ability_router_find_one_success(client, trainer, token, pokemon_ability):
        with patch(
            'app.domain.ability.service.PokemonAbilityService.find_one_cached',
            new_callable=AsyncMock,
        ) as mock_fetch:
            mock_fetch.return_value = pokemon_ability

            response = client.get(
                f'/ability/{pokemon_ability.id}',
                headers={'Authorization': f'Bearer {token}'},
            )
            assert response.status_code == HTTPStatus.OK
            data = response.json()
            assert isinstance(data, dict)
            assert data['name'] == pokemon_ability.name
