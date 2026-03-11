from http import HTTPStatus
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from fastapi import HTTPException

from app.domain.pokemon.external.business import PokemonExternalBusiness
from app.domain.pokemon.external.schemas import (
    PokemonExternalBaseSchemaResponse,
    PokemonExternalGrowthRateSchemaResponse,
    PokemonExternalMoveSchemaResponse,
    PokemonExternalTypeSchemaResponse,
)
from app.domain.pokemon.external.schemas.evolution import (
    PokemonExternalEvolutionSchemaResponse,
)
from app.domain.pokemon.external.schemas.fetch_one import (
    PokemonFetchOneSchemaResponse,
)
from app.domain.pokemon.external.schemas.name import (
    PokemonExternalByNameSchemaResponse,
)
from app.domain.pokemon.external.schemas.specie import (
    PokemonExternalSpecieSchemaResponse,
)
from app.domain.pokemon.external.service import PokemonExternalService
from tests.app.domain.pokemon.external.mocks.business_mock import (
    MOCK_ATTRIBUTES_ATTACK,
    MOCK_ATTRIBUTES_BASE_EXPERIENCE,
    MOCK_ATTRIBUTES_DEFENSE,
    MOCK_ATTRIBUTES_HEIGHT,
    MOCK_ATTRIBUTES_HP,
    MOCK_ATTRIBUTES_SPECIAL_ATTACK,
    MOCK_ATTRIBUTES_SPECIAL_DEFENSE,
    MOCK_ATTRIBUTES_SPEED,
    MOCK_ATTRIBUTES_WEIGHT,
    MOCK_BUSINESS_ENSURE_ATTRIBUTES,
    MOCK_BUSINESS_SPECIE_ENSURE_ATTRIBUTES,
)
from tests.app.domain.pokemon.external.mocks.external_mock import (
    MOCK_INITIAL_POKEMON,
    MOCK_POKEMON_IMAGE,
    MOCK_POKEMON_NAME,
    MOCK_RESPONSE_BY_EVOLUTION_ORDER_DATA,
    MOCK_RESPONSE_BY_GROWTH_RATE_DATA,
    MOCK_RESPONSE_BY_MOVE_DATA,
    MOCK_RESPONSE_BY_NAME,
    MOCK_RESPONSE_BY_NAME_DATA,
    MOCK_RESPONSE_BY_SPECIE,
    MOCK_RESPONSE_BY_SPECIE_DATA,
    MOCK_RESPONSE_BY_TYPE_DATA,
)


class TestPokemonExternalServiceList:
    """Test scope for pokemon_external_list method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_external_list_success():
        """Should return list of pokemon when API request is successful"""
        expected_list_size = 2
        offset = 0
        limit = 2
        expected_first_order = 1
        expected_second_order = 2

        mock_response_data = {
            'results': [
                {
                    'name': 'bulbasaur',
                    'url': 'https://pokeapi.co/api/v2/pokemon/1/',
                },
                {
                    'name': 'ivysaur',
                    'url': 'https://pokeapi.co/api/v2/pokemon/2/',
                },
            ]
        }

        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status.return_value = None

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = AsyncMock()
            mock_client.get.return_value = mock_response
            mock_client_class.return_value = mock_client

            result = await PokemonExternalService.pokemon_external_list(
                offset=offset, limit=limit
            )

            assert isinstance(result, list)
            assert len(result) == expected_list_size
            assert all(isinstance(item, PokemonExternalBaseSchemaResponse) for item in result)
            assert result[0].name == 'bulbasaur'
            assert result[0].order == expected_first_order
            assert result[1].name == 'ivysaur'
            assert result[1].order == expected_second_order

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_external_list_empty_results():
        """Should return empty list when results are empty"""
        expected_list_size = 0
        offset = 0
        limit = 2

        mock_response_data = {'results': []}

        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status.return_value = None

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = AsyncMock()
            mock_client.get.return_value = mock_response
            mock_client_class.return_value = mock_client

            result = await PokemonExternalService.pokemon_external_list(
                offset=offset, limit=limit
            )

            assert isinstance(result, list)
            assert len(result) == expected_list_size

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_external_list_no_results_key():
        """Should raise HTTPException when results key is missing"""
        offset = 0
        limit = 2

        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_response.raise_for_status.return_value = None
        text_detail = 'Failed to execute external request'

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.get.return_value = mock_response
            mock_client_class.return_value = mock_client

            with pytest.raises(HTTPException) as exc_info:
                await PokemonExternalService.pokemon_external_list(offset=offset, limit=limit)

        assert exc_info.value.status_code == HTTPStatus.SERVICE_UNAVAILABLE
        assert text_detail in exc_info.value.detail

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_external_list_http_error():
        """Should raise HTTPException when HTTP request fails"""
        offset = 0
        limit = 2

        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_response.raise_for_status.return_value = None
        text_detail = 'Failed to execute external request'

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.get.side_effect = httpx.HTTPError('Connection error')
            mock_client_class.return_value = mock_client

            with pytest.raises(HTTPException) as exc_info:
                await PokemonExternalService.pokemon_external_list(offset=offset, limit=limit)

        assert exc_info.value.status_code == HTTPStatus.SERVICE_UNAVAILABLE
        assert text_detail in exc_info.value.detail


class TestPokemonExternalServiceByName:
    """Test scope for pokemon_external_by_name method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_external_by_name_success():
        """Should return pokemon data when API request is successful"""
        total_stats = 6

        mock_response_data = MOCK_RESPONSE_BY_NAME_DATA
        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status.return_value = None
        mock_response.__bool__.return_value = True

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.get.return_value = mock_response
            mock_client_class.return_value = mock_client

            result = await PokemonExternalService.pokemon_external_by_name(MOCK_POKEMON_NAME)

            assert isinstance(result, PokemonExternalByNameSchemaResponse)
            assert result.name == MOCK_RESPONSE_BY_NAME.name
            assert result.order == mock_response_data['order']
            assert result.height == mock_response_data['height']
            assert result.weight == mock_response_data['weight']
            assert result.base_experience == mock_response_data['base_experience']
            assert len(result.types) == 1
            assert len(result.moves) == 1
            assert len(result.abilities) == 1
            assert len(result.stats) == total_stats
            assert result.sprites.front_default == MOCK_POKEMON_IMAGE

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_external_by_name_no_name_key():
        """Should return None when name key is missing in response"""

        mock_response_data = {}

        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status.return_value = None
        mock_response.__bool__.return_value = True

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.get.return_value = mock_response
            mock_client_class.return_value = mock_client

            result = await PokemonExternalService.pokemon_external_by_name('invalid')

            assert result is None

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_external_by_name_http_error():
        """Should raise HTTPException when HTTP request fails"""
        text_detail = 'Failed to execute external request'

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.get.side_effect = httpx.HTTPError('Connection error')
            mock_client_class.return_value = mock_client

            with pytest.raises(HTTPException) as exc_info:
                await PokemonExternalService.pokemon_external_by_name('invalid')

        assert exc_info.value.status_code == HTTPStatus.SERVICE_UNAVAILABLE
        assert text_detail in exc_info.value.detail


class TestPokemonExternalServiceBySpecie:
    """Test scope for pokemon_external_by_specie method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_external_by_specie_success():
        """Should return pokemon data when API request is successful"""

        mock_response_data = MOCK_RESPONSE_BY_SPECIE_DATA
        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status.return_value = None
        mock_response.__bool__.return_value = True

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.get.return_value = mock_response
            mock_client_class.return_value = mock_client

            result = await PokemonExternalService.pokemon_external_specie_by_name(
                MOCK_POKEMON_NAME
            )

            assert isinstance(result, PokemonExternalSpecieSchemaResponse)
            assert result.name == mock_response_data['name']
            assert result.is_baby == mock_response_data['is_baby']
            assert result.is_legendary == mock_response_data['is_legendary']
            assert result.is_mythical == mock_response_data['is_mythical']

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_external_by_specie_no_name_key():
        """Should return None when name key is missing in response"""

        mock_response_data = {}

        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status.return_value = None
        mock_response.__bool__.return_value = True

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.get.return_value = mock_response
            mock_client_class.return_value = mock_client

            result = await PokemonExternalService.pokemon_external_specie_by_name('invalid')

            assert result is None

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_external_by_specie_http_error():
        """Should raise HTTPException when HTTP request fails"""
        text_detail = 'Failed to execute external request'

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.get.side_effect = httpx.HTTPError('Connection error')
            mock_client_class.return_value = mock_client

            with pytest.raises(HTTPException) as exc_info:
                await PokemonExternalService.pokemon_external_specie_by_name('invalid')

        assert exc_info.value.status_code == HTTPStatus.SERVICE_UNAVAILABLE
        assert text_detail in exc_info.value.detail


class TestPokemonExternalServiceByMoveName:
    """Test scope for pokemon_external_by_move method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_external_by_move_success():
        """Should return pokemon data when API request is successful"""

        name = 'cut'
        mock_response_data = MOCK_RESPONSE_BY_MOVE_DATA
        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status.return_value = None
        mock_response.__bool__.return_value = True

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.get.return_value = mock_response
            mock_client_class.return_value = mock_client

            result = await PokemonExternalService.pokemon_external_move_by_name(name)

            assert isinstance(result, PokemonExternalMoveSchemaResponse)
            assert result.name == mock_response_data['name']
            assert result.accuracy == mock_response_data['accuracy']
            assert result.id == mock_response_data['id']
            assert result.power == mock_response_data['power']
            assert result.pp == mock_response_data['pp']
            assert result.priority == mock_response_data['priority']
            assert len(result.effect_changes) == len(mock_response_data['effect_changes'])
            assert len(result.effect_entries) == len(mock_response_data['effect_entries'])
            assert len(result.learned_by_pokemon) == len(
                mock_response_data['learned_by_pokemon']
            )
            assert len(result.machines) == len(mock_response_data['machines'])
            assert len(result.names) == len(mock_response_data['names'])

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_external_by_move_no_name_key():
        """Should return None when name key is missing in response"""

        mock_response_data = {}

        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status.return_value = None
        mock_response.__bool__.return_value = True

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.get.return_value = mock_response
            mock_client_class.return_value = mock_client

            result = await PokemonExternalService.pokemon_external_move_by_name('invalid')

            assert result is None

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_external_by_move_http_error():
        """Should raise HTTPException when HTTP request fails"""
        text_detail = 'Failed to execute external request'

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.get.side_effect = httpx.HTTPError('Connection error')
            mock_client_class.return_value = mock_client

            with pytest.raises(HTTPException) as exc_info:
                await PokemonExternalService.pokemon_external_move_by_name('invalid')

        assert exc_info.value.status_code == HTTPStatus.SERVICE_UNAVAILABLE
        assert text_detail in exc_info.value.detail


class TestPokemonExternalServiceByGrowthRateOrder:
    """Test scope for pokemon_external_growth_rate_by_order method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_external_by_growth_rate_order_success():
        """Should return pokemon data when API request is successful"""

        mock_response_data = MOCK_RESPONSE_BY_GROWTH_RATE_DATA
        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status.return_value = None
        mock_response.__bool__.return_value = True

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.get.return_value = mock_response
            mock_client_class.return_value = mock_client

            result = await PokemonExternalService.pokemon_external_growth_rate_by_order(2)

            assert isinstance(result, PokemonExternalGrowthRateSchemaResponse)
            assert result.name == mock_response_data['name']
            assert result.id == mock_response_data['id']
            assert result.formula == mock_response_data['formula']
            assert len(result.levels) == len(mock_response_data['levels'])
            assert len(result.descriptions) == len(mock_response_data['descriptions'])

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_external_by_growth_rate_order_no_name_key():
        """Should return None when name key is missing in response"""

        mock_response_data = {}

        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status.return_value = None
        mock_response.__bool__.return_value = True

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.get.return_value = mock_response
            mock_client_class.return_value = mock_client

            result = await PokemonExternalService.pokemon_external_growth_rate_by_order(0)

            assert result is None

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_external_by_growth_rate_order_http_error():
        """Should raise HTTPException when HTTP request fails"""
        text_detail = 'Failed to execute external request'

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.get.side_effect = httpx.HTTPError('Connection error')
            mock_client_class.return_value = mock_client

            with pytest.raises(HTTPException) as exc_info:
                await PokemonExternalService.pokemon_external_growth_rate_by_order(0)

        assert exc_info.value.status_code == HTTPStatus.SERVICE_UNAVAILABLE
        assert text_detail in exc_info.value.detail


class TestPokemonExternalServiceByEvolutionUrl:
    """Test scope for pokemon_external_evolution_by_url method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_external_by_evolution_url_success():
        """Should return pokemon data when API request is successful"""

        mock_response_data = MOCK_RESPONSE_BY_EVOLUTION_ORDER_DATA
        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status.return_value = None
        mock_response.__bool__.return_value = True

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.get.return_value = mock_response
            mock_client_class.return_value = mock_client

            result = await PokemonExternalService.pokemon_external_evolution_by_url(
                'https://pokeapi.co/api/v2/evolution-chain/1/'
            )

            assert isinstance(result, PokemonExternalEvolutionSchemaResponse)
            assert result.id == mock_response_data['id']
            assert len(result.chain.evolves_to) == len(
                mock_response_data['chain']['evolves_to']
            )
            assert len(result.chain.evolution_details) == len(
                mock_response_data['chain']['evolution_details']
            )
            assert result.chain.is_baby is mock_response_data['chain']['is_baby']
            assert result.chain.species.name == 'bulbasaur'
            assert result.baby_trigger_item is mock_response_data['baby_trigger_item']

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_external_by_evolution_url_no_name_key():
        """Should return None when name key is missing in response"""

        mock_response_data = {}

        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status.return_value = None
        mock_response.__bool__.return_value = True

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.get.return_value = mock_response
            mock_client_class.return_value = mock_client

            result = await PokemonExternalService.pokemon_external_evolution_by_url(
                'https://pokeapi.co/api/v2/evolution-chain/1/'
            )

            assert result is None

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_external_by_evolution_url_http_error():
        """Should raise HTTPException when HTTP request fails"""
        text_detail = 'Failed to execute external request'

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.get.side_effect = httpx.HTTPError('Connection error')
            mock_client_class.return_value = mock_client

            with pytest.raises(HTTPException) as exc_info:
                await PokemonExternalService.pokemon_external_evolution_by_url(
                    'https://pokeapi.co/api/v2/evolution-chain/1/'
                )

        assert exc_info.value.status_code == HTTPStatus.SERVICE_UNAVAILABLE
        assert text_detail in exc_info.value.detail


class TestPokemonExternalServiceByTypeUrl:
    """Test scope for pokemon_external_evolution_by_url method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_external_by_type_url_success():
        """Should return pokemon type data when API request is successful"""

        mock_response_data = MOCK_RESPONSE_BY_TYPE_DATA
        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status.return_value = None
        mock_response.__bool__.return_value = True

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.get.return_value = mock_response
            mock_client_class.return_value = mock_client

            result = await PokemonExternalService.pokemon_external_type_by_url(
                'https://pokeapi.co/api/v2/type/10/'
            )

            assert isinstance(result, PokemonExternalTypeSchemaResponse)
            assert result.id == mock_response_data['id']
            damage_relations = result.damage_relations
            assert len(damage_relations.double_damage_from) == len(
                mock_response_data['damage_relations']['double_damage_from']
            )
            assert len(damage_relations.double_damage_to) == len(
                mock_response_data['damage_relations']['double_damage_to']
            )
            assert len(damage_relations.half_damage_from) == len(
                mock_response_data['damage_relations']['half_damage_from']
            )
            assert len(damage_relations.half_damage_to) == len(
                mock_response_data['damage_relations']['half_damage_to']
            )

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_external_by_type_url_no_name_key():
        """Should return None when name key is missing in response"""

        mock_response_data = {}

        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status.return_value = None
        mock_response.__bool__.return_value = True

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.get.return_value = mock_response
            mock_client_class.return_value = mock_client

            result = await PokemonExternalService.pokemon_external_type_by_url(
                'https://pokeapi.co/api/v2/type/10/'
            )

            assert result is None

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_external_by_type_url_http_error():
        """Should raise HTTPException when HTTP request fails"""
        text_detail = 'Failed to execute external request'

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.get.side_effect = httpx.HTTPError('Connection error')
            mock_client_class.return_value = mock_client

            with pytest.raises(HTTPException) as exc_info:
                await PokemonExternalService.pokemon_external_type_by_url(
                    'https://pokeapi.co/api/v2/type/10/'
                )

        assert exc_info.value.status_code == HTTPStatus.SERVICE_UNAVAILABLE
        assert text_detail in exc_info.value.detail


class TestPokemonExternalServiceFetchByName:
    """Test scope for fetch_by_name method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_external_fetch_by_name_not_pokemon_name():
        """Should return pokemon data when API request is not pokemon name"""
        with patch.object(
            PokemonExternalService,
            'pokemon_external_by_name',
            new_callable=AsyncMock,
            return_value=None,
        ):
            result = await PokemonExternalService.fetch_by_name(MOCK_INITIAL_POKEMON)

        assert isinstance(result, PokemonFetchOneSchemaResponse)
        assert result.pokemon.url == MOCK_INITIAL_POKEMON.url
        assert result.pokemon.name == MOCK_POKEMON_NAME
        assert result.pokemon.order == MOCK_INITIAL_POKEMON.order
        assert result.pokemon.external_image == MOCK_INITIAL_POKEMON.external_image
        assert not result.pokemon.hp
        assert not result.pokemon.image
        assert not result.pokemon.speed
        assert not result.pokemon.height
        assert not result.pokemon.weight
        assert not result.pokemon.attack
        assert not result.pokemon.defense
        assert not result.pokemon.habitat
        assert not result.pokemon.is_baby
        assert not result.pokemon.shape_url
        assert not result.pokemon.shape_name
        assert not result.pokemon.is_mythical
        assert not result.pokemon.gender_rate
        assert not result.pokemon.is_legendary
        assert not result.pokemon.capture_rate
        assert not result.pokemon.hatch_counter
        assert not result.pokemon.base_happiness
        assert not result.pokemon.base_experience
        assert not result.pokemon.special_attack
        assert not result.pokemon.special_defense
        assert not result.pokemon.evolution_chain_url
        assert not result.pokemon.evolves_from_species
        assert not result.pokemon.has_gender_differences
        assert len(result.types) == 0
        assert len(result.moves) == 0
        assert len(result.abilities) == 0

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_external_fetch_by_name_not_pokemon_specie():
        """Should return pokemon data when API request is not pokemon specie"""

        with (
            patch.object(
                PokemonExternalService,
                'pokemon_external_by_name',
                new_callable=AsyncMock,
                return_value=MOCK_RESPONSE_BY_NAME,
            ),
            patch.object(
                PokemonExternalService,
                'pokemon_external_specie_by_name',
                new_callable=AsyncMock,
                return_value=None,
            ),
            patch.object(
                PokemonExternalBusiness,
                'ensure_image',
                return_value=MOCK_RESPONSE_BY_NAME.sprites.front_default,
            ),
            patch.object(
                PokemonExternalBusiness,
                'ensure_attributes',
                return_value=MOCK_BUSINESS_ENSURE_ATTRIBUTES,
            ),
        ):
            result = await PokemonExternalService.fetch_by_name(MOCK_INITIAL_POKEMON)

        assert isinstance(result, PokemonFetchOneSchemaResponse)
        assert result.pokemon.url == MOCK_INITIAL_POKEMON.url
        assert result.pokemon.name == MOCK_POKEMON_NAME
        assert result.pokemon.order == MOCK_INITIAL_POKEMON.order
        assert result.pokemon.external_image == MOCK_INITIAL_POKEMON.external_image
        assert result.pokemon.hp == MOCK_ATTRIBUTES_HP
        assert result.pokemon.image == MOCK_RESPONSE_BY_NAME.sprites.front_default
        assert result.pokemon.speed == MOCK_ATTRIBUTES_SPEED
        assert result.pokemon.height == MOCK_ATTRIBUTES_HEIGHT
        assert result.pokemon.weight == MOCK_ATTRIBUTES_WEIGHT
        assert result.pokemon.attack == MOCK_ATTRIBUTES_ATTACK
        assert result.pokemon.defense == MOCK_ATTRIBUTES_DEFENSE
        assert not result.pokemon.habitat
        assert not result.pokemon.is_baby
        assert not result.pokemon.shape_url
        assert not result.pokemon.shape_name
        assert not result.pokemon.is_mythical
        assert not result.pokemon.gender_rate
        assert not result.pokemon.is_legendary
        assert not result.pokemon.capture_rate
        assert not result.pokemon.hatch_counter
        assert not result.pokemon.base_happiness
        assert result.pokemon.base_experience == MOCK_ATTRIBUTES_BASE_EXPERIENCE
        assert result.pokemon.special_attack == MOCK_ATTRIBUTES_SPECIAL_ATTACK
        assert result.pokemon.special_defense == MOCK_ATTRIBUTES_SPECIAL_DEFENSE
        assert not result.pokemon.evolution_chain_url
        assert not result.pokemon.evolves_from_species
        assert not result.pokemon.has_gender_differences
        assert len(result.types) == len(MOCK_RESPONSE_BY_NAME.types)
        assert len(result.moves) == len(MOCK_RESPONSE_BY_NAME.moves)
        assert len(result.abilities) == len(MOCK_RESPONSE_BY_NAME.abilities)

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_external_fetch_by_name_success():
        """Should return pokemon data when API request is successful"""
        pokemon_hp = 10

        mock_attributes = MagicMock()
        mock_attributes.hp = pokemon_hp
        mock_attributes.speed = 10
        mock_attributes.attack = 10
        mock_attributes.defense = 10
        mock_attributes.special_attack = 10
        mock_attributes.special_defense = 10
        mock_attributes.height = 10
        mock_attributes.weight = 10
        mock_attributes.base_experience = 10

        with (
            patch.object(
                PokemonExternalService,
                'pokemon_external_by_name',
                new_callable=AsyncMock,
                return_value=MOCK_RESPONSE_BY_NAME,
            ),
            patch.object(
                PokemonExternalService,
                'pokemon_external_specie_by_name',
                new_callable=AsyncMock,
                return_value=MOCK_RESPONSE_BY_SPECIE,
            ),
            patch.object(
                PokemonExternalBusiness,
                'ensure_image',
                return_value=MOCK_RESPONSE_BY_NAME.sprites.front_default,
            ),
            patch.object(
                PokemonExternalBusiness,
                'ensure_attributes',
                return_value=MOCK_BUSINESS_ENSURE_ATTRIBUTES,
            ),
            patch.object(
                PokemonExternalBusiness,
                'ensure_specie_attributes',
                return_value=MOCK_BUSINESS_SPECIE_ENSURE_ATTRIBUTES,
            ),
        ):
            result = await PokemonExternalService.fetch_by_name(MOCK_INITIAL_POKEMON)

        assert isinstance(result, PokemonFetchOneSchemaResponse)
        assert result.pokemon.url == MOCK_INITIAL_POKEMON.url
        assert result.pokemon.name == MOCK_POKEMON_NAME
        assert result.pokemon.order == MOCK_INITIAL_POKEMON.order
        assert result.pokemon.external_image == MOCK_INITIAL_POKEMON.external_image
        assert result.pokemon.hp == MOCK_ATTRIBUTES_HP
        assert result.pokemon.image == MOCK_RESPONSE_BY_NAME.sprites.front_default
        assert result.pokemon.speed == MOCK_ATTRIBUTES_SPEED
        assert result.pokemon.height == MOCK_ATTRIBUTES_HEIGHT
        assert result.pokemon.weight == MOCK_ATTRIBUTES_WEIGHT
        assert result.pokemon.attack == MOCK_ATTRIBUTES_ATTACK
        assert result.pokemon.defense == MOCK_ATTRIBUTES_DEFENSE
        assert result.pokemon.habitat == MOCK_BUSINESS_SPECIE_ENSURE_ATTRIBUTES.habitat
        assert result.pokemon.is_baby == MOCK_BUSINESS_SPECIE_ENSURE_ATTRIBUTES.is_baby
        assert result.pokemon.shape_url == MOCK_BUSINESS_SPECIE_ENSURE_ATTRIBUTES.shape_url
        assert result.pokemon.shape_name == MOCK_BUSINESS_SPECIE_ENSURE_ATTRIBUTES.shape_name
        assert result.pokemon.is_mythical == MOCK_BUSINESS_SPECIE_ENSURE_ATTRIBUTES.is_mythical
        assert result.pokemon.gender_rate == MOCK_BUSINESS_SPECIE_ENSURE_ATTRIBUTES.gender_rate
        assert (
            result.pokemon.is_legendary == MOCK_BUSINESS_SPECIE_ENSURE_ATTRIBUTES.is_legendary
        )
        assert (
            result.pokemon.capture_rate == MOCK_BUSINESS_SPECIE_ENSURE_ATTRIBUTES.capture_rate
        )
        assert (
            result.pokemon.hatch_counter
            == MOCK_BUSINESS_SPECIE_ENSURE_ATTRIBUTES.hatch_counter
        )
        assert (
            result.pokemon.base_happiness
            == MOCK_BUSINESS_SPECIE_ENSURE_ATTRIBUTES.base_happiness
        )
        assert result.pokemon.base_experience == MOCK_ATTRIBUTES_BASE_EXPERIENCE
        assert result.pokemon.special_attack == MOCK_ATTRIBUTES_SPECIAL_ATTACK
        assert result.pokemon.special_defense == MOCK_ATTRIBUTES_SPECIAL_DEFENSE
        assert (
            result.pokemon.evolution_chain_url
            == MOCK_BUSINESS_SPECIE_ENSURE_ATTRIBUTES.evolution_chain_url
        )
        assert (
            result.pokemon.evolves_from_species
            == MOCK_BUSINESS_SPECIE_ENSURE_ATTRIBUTES.evolves_from_species
        )
        assert (
            result.pokemon.has_gender_differences
            == MOCK_BUSINESS_SPECIE_ENSURE_ATTRIBUTES.has_gender_differences
        )
        assert len(result.types) == len(MOCK_RESPONSE_BY_NAME.types)
        assert len(result.moves) == len(MOCK_RESPONSE_BY_NAME.moves)
        assert len(result.abilities) == len(MOCK_RESPONSE_BY_NAME.abilities)
        assert result.growth_rate.url == MOCK_RESPONSE_BY_SPECIE.growth_rate.url
        assert result.growth_rate.name == MOCK_RESPONSE_BY_SPECIE.growth_rate.name

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_external_fetch_by_name_http_error():
        """Should raise HTTPException when HTTP request fails"""
        text_detail = 'Failed to execute external request'
        with patch.object(
            PokemonExternalService,
            'pokemon_external_by_name',
            new_callable=AsyncMock,
            side_effect=httpx.HTTPError('Connection error'),
        ):
            with pytest.raises(HTTPException) as exc_info:
                await PokemonExternalService.fetch_by_name(MOCK_INITIAL_POKEMON)

            assert exc_info.value.status_code == HTTPStatus.SERVICE_UNAVAILABLE
            assert text_detail in exc_info.value.detail
