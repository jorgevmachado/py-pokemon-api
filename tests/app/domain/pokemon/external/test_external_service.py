from http import HTTPStatus
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from fastapi import HTTPException

from app.domain.pokemon.external.schemas import (
    PokemonExternalBaseSchemaResponse,
)
from app.domain.pokemon.external.schemas.name import (
    PokemonExternalByNameSchemaResponse,
)
from app.domain.pokemon.external.service import PokemonExternalService


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
            assert all(
                isinstance(item, PokemonExternalBaseSchemaResponse)
                for item in result
            )
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
        text_detail = 'Failed to execute external request:(list)'

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = False
            mock_client.get.return_value = mock_response
            mock_client_class.return_value = mock_client

            with pytest.raises(HTTPException) as exc_info:
                await PokemonExternalService.pokemon_external_list(
                    offset=offset, limit=limit
                )

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
        text_detail = 'Failed to execute external request:(list)'

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = False
            mock_client.get.side_effect = httpx.HTTPError('Connection error')
            mock_client_class.return_value = mock_client

            with pytest.raises(HTTPException) as exc_info:
                await PokemonExternalService.pokemon_external_list(
                    offset=offset, limit=limit
                )

        assert exc_info.value.status_code == HTTPStatus.SERVICE_UNAVAILABLE
        assert text_detail in exc_info.value.detail


class TestPokemonExternalServiceByName:
    """Test scope for pokemon_external_by_name method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_external_by_name_success():
        """Should return pokemon data when API request is successful"""

        order = 1
        name = 'bulbasaur'
        height = 7
        weight = 69
        base_experience = 64
        image = 'https://example.com/bulbasaur.png'

        mock_response_data = {
            'name': 'bulbasaur',
            'order': order,
            'height': height,
            'weight': weight,
            'base_experience': base_experience,
            'types': [],
            'moves': [],
            'stats': [],
            'abilities': [],
            'sprites': {'front_default': image},
        }

        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status.return_value = None
        mock_response.__bool__.return_value = True

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = False
            mock_client.get.return_value = mock_response
            mock_client_class.return_value = mock_client

            result = await PokemonExternalService.pokemon_external_by_name(
                name
            )

            assert isinstance(result, PokemonExternalByNameSchemaResponse)
            assert result.name == name
            assert result.order == order
            assert result.height == height
            assert result.weight == weight
            assert result.base_experience == base_experience

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

            result = await PokemonExternalService.pokemon_external_by_name(
                'invalid'
            )

            assert result is None

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokemon_external_by_name_http_error():
        """Should raise HTTPException when HTTP request fails"""
        text_detail = 'Failed to execute external request:(name)'

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = False
            mock_client.get.side_effect = httpx.HTTPError('Connection error')
            mock_client_class.return_value = mock_client

            with pytest.raises(HTTPException) as exc_info:
                await PokemonExternalService.pokemon_external_by_name(
                    'invalid'
                )

        assert exc_info.value.status_code == HTTPStatus.SERVICE_UNAVAILABLE
        assert text_detail in exc_info.value.detail
