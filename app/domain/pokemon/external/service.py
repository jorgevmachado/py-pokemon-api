from http import HTTPStatus

import httpx
from fastapi import HTTPException

from app.domain.pokemon.external.schemas import (
    PokemonExternalBaseSchemaResponse,
)
from app.domain.pokemon.external.schemas.name import (
    PokemonExternalByNameSchemaResponse,
)
from app.shared.image import ensure_external_image
from app.shared.number import ensure_order_number


class PokemonExternalService:
    BASE_URL = 'https://pokeapi.co/api/v2'

    @staticmethod
    async def pokemon_external_list(
        offset: int, limit: int
    ) -> list[PokemonExternalBaseSchemaResponse]:
        try:
            async with httpx.AsyncClient(verify=False) as client:
                response = await client.get(
                    f'{PokemonExternalService.BASE_URL}/pokemon',
                    params={'limit': limit, 'offset': offset},
                    timeout=10.0,
                )
                response.raise_for_status()
                response_data = response.json()

                if 'results' not in response_data:
                    raise HTTPException(
                        status_code=HTTPStatus.SERVICE_UNAVAILABLE,
                        detail='Failed to execute external request:(list).',
                    )

                results = response_data['results']
                new_results = [
                    {
                        **item,
                        'order': ensure_order_number(item.get('url')),
                        'external_image': ensure_external_image(
                            ensure_order_number(item.get('url'))
                        ),
                    }
                    for item in results
                ]
                return [
                    PokemonExternalBaseSchemaResponse(**item)
                    for item in new_results
                ]
        except HTTPException:
            raise
        except httpx.HTTPError as e:
            print(f'# => pokemon_external_list => error => {e}')
            raise HTTPException(
                status_code=HTTPStatus.SERVICE_UNAVAILABLE,
                detail='Failed to execute external request:(list).',
            )

    @staticmethod
    async def pokemon_external_by_name(
        name: str,
    ) -> PokemonExternalByNameSchemaResponse | None:
        try:
            async with httpx.AsyncClient(verify=False) as client:
                response = await client.get(
                    f'{PokemonExternalService.BASE_URL}/pokemon/{name}',
                    timeout=10.0,
                )
                response.raise_for_status()
                response_data = response.json()

                if not response_data or 'name' not in response_data:
                    return None

                return PokemonExternalByNameSchemaResponse(**response_data)
        except httpx.HTTPError as e:
            print(f'# => pokemon_external_by_name => error => {e}')
            raise HTTPException(
                status_code=HTTPStatus.SERVICE_UNAVAILABLE,
                detail='Failed to execute external request:(name).',
            )
