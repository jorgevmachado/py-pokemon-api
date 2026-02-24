from http import HTTPStatus

import httpx
from fastapi import HTTPException

from app.domain.pokemon.external.business import PokemonExternalBusiness
from app.domain.pokemon.external.schemas import (
    PokemonExternalBaseSchemaResponse,
    PokemonExternalEvolutionSchemaResponse,
    PokemonExternalGrowthRateSchemaResponse,
)
from app.domain.pokemon.external.schemas.fetch_one import PokemonFetchOneSchemaResponse
from app.domain.pokemon.external.schemas.move import (
    PokemonExternalMoveSchemaResponse,
)
from app.domain.pokemon.external.schemas.name import (
    PokemonExternalByNameSchemaResponse,
)
from app.domain.pokemon.external.schemas.specie import (
    PokemonExternalSpecieSchemaResponse,
)
from app.domain.pokemon.schema import PokemonSchema
from app.shared.image import ensure_external_image
from app.shared.number import ensure_order_number
from app.shared.status_enum import StatusEnum


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
                return [PokemonExternalBaseSchemaResponse(**item) for item in new_results]
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

    @staticmethod
    async def pokemon_external_specie_by_name(
        name: str,
    ) -> PokemonExternalSpecieSchemaResponse | None:
        try:
            async with httpx.AsyncClient(verify=False) as client:
                response = await client.get(
                    f'{PokemonExternalService.BASE_URL}/pokemon-species/{name}',
                    timeout=10.0,
                )
                response.raise_for_status()
                response_data = response.json()

                if not response_data or 'name' not in response_data:
                    return None

                return PokemonExternalSpecieSchemaResponse(**response_data)
        except httpx.HTTPError as e:
            print(f'# => pokemon_external_specie_by_name => error => {e}')
            raise HTTPException(
                status_code=HTTPStatus.SERVICE_UNAVAILABLE,
                detail='Failed to execute external request:(specie).',
            )

    @staticmethod
    async def pokemon_external_move_by_name(
        name: str,
    ) -> PokemonExternalMoveSchemaResponse | None:
        try:
            async with httpx.AsyncClient(verify=False) as client:
                response = await client.get(
                    f'{PokemonExternalService.BASE_URL}/move/{name}',
                    timeout=10.0,
                )
                response.raise_for_status()
                response_data = response.json()

                if not response_data or 'name' not in response_data:
                    return None

                return PokemonExternalMoveSchemaResponse(**response_data)
        except httpx.HTTPError as e:
            print(f'# => pokemon_external_move_by_name => error => {e}')
            raise HTTPException(
                status_code=HTTPStatus.SERVICE_UNAVAILABLE,
                detail='Failed to execute external request:(move).',
            )

    @staticmethod
    async def pokemon_external_growth_rate_by_order(
        order: int,
    ) -> PokemonExternalGrowthRateSchemaResponse | None:
        try:
            async with httpx.AsyncClient(verify=False) as client:
                response = await client.get(
                    f'{PokemonExternalService.BASE_URL}/growth-rate/{order}',
                    timeout=10.0,
                )
                response.raise_for_status()
                response_data = response.json()
                if not response_data or 'name' not in response_data:
                    return None
                return PokemonExternalGrowthRateSchemaResponse(**response_data)
        except httpx.HTTPError as e:
            print(f'# => pokemon_external_growth_rate_by_order => error => {e}')
            raise HTTPException(
                status_code=HTTPStatus.SERVICE_UNAVAILABLE,
                detail='Failed to execute external request:(growth_rate).',
            )

    @staticmethod
    async def pokemon_external_evolution_by_order(
        order: int,
    ) -> PokemonExternalEvolutionSchemaResponse | None:
        try:
            async with httpx.AsyncClient(verify=False) as client:
                response = await client.get(
                    f'{PokemonExternalService.BASE_URL}/evolution-chain/{order}',
                    timeout=10.0,
                )
                response.raise_for_status()
                response_data = response.json()
                if not response_data or 'id' not in response_data:
                    return None
                return PokemonExternalEvolutionSchemaResponse(**response_data)
        except httpx.HTTPError as e:
            print(f'# => pokemon_external_evolution_by_order => error => {e}')
            raise HTTPException(
                status_code=HTTPStatus.SERVICE_UNAVAILABLE,
                detail='Failed to execute external request:(evolution_chain).',
            )

    @staticmethod
    async def fetch_by_name(
        pokemon: PokemonSchema,
    ) -> PokemonFetchOneSchemaResponse | None:
        try:
            pokemon_name_response = await PokemonExternalService.pokemon_external_by_name(
                pokemon.name
            )
            if pokemon_name_response is None:
                return PokemonFetchOneSchemaResponse(
                    pokemon=pokemon,
                    types=[],
                    moves=[],
                    abilities=[],
                )
            types = pokemon_name_response.types
            moves = pokemon_name_response.moves
            abilities = pokemon_name_response.abilities
            attributes = PokemonExternalBusiness.ensure_attributes(pokemon_name_response)

            pokemon_with_pokemon_name = PokemonSchema(
                url=pokemon.url,
                name=pokemon.name,
                order=pokemon.order,
                status=StatusEnum.INCOMPLETE,
                external_image=pokemon.external_image,
                hp=attributes.hp,
                image=PokemonExternalBusiness.ensure_image(pokemon_name_response.sprites),
                speed=attributes.speed,
                height=attributes.height,
                weight=attributes.weight,
                attack=attributes.attack,
                defense=attributes.defense,
                habitat=None,
                is_baby=False,
                shape_url=None,
                shape_name=None,
                is_mythical=False,
                gender_rate=None,
                is_legendary=False,
                capture_rate=None,
                hatch_counter=None,
                base_happiness=None,
                special_attack=attributes.special_attack,
                base_experience=attributes.base_experience,
                special_defense=attributes.special_defense,
                evolution_chain_url=None,
                evolves_from_species=None,
                has_gender_differences=False,
            )

            pokemon_specie_response = await (
                PokemonExternalService.pokemon_external_specie_by_name(pokemon.name)
            )

            if pokemon_specie_response is None:
                return PokemonFetchOneSchemaResponse(
                    pokemon=pokemon_with_pokemon_name,
                    types=types,
                    moves=moves,
                    abilities=abilities,
                )

            specie_attributes = PokemonExternalBusiness.ensure_specie_attributes(
                pokemon_specie_response
            )

            return PokemonFetchOneSchemaResponse(
                pokemon=PokemonSchema(
                    url=pokemon_with_pokemon_name.url,
                    name=pokemon_with_pokemon_name.name,
                    order=pokemon_with_pokemon_name.order,
                    status=StatusEnum.INCOMPLETE,
                    external_image=pokemon_with_pokemon_name.external_image,
                    hp=attributes.hp,
                    image=PokemonExternalBusiness.ensure_image(
                        pokemon_with_pokemon_name.image
                    ),
                    speed=pokemon_with_pokemon_name.speed,
                    height=pokemon_with_pokemon_name.height,
                    weight=pokemon_with_pokemon_name.weight,
                    attack=pokemon_with_pokemon_name.attack,
                    defense=pokemon_with_pokemon_name.defense,
                    habitat=specie_attributes.habitat,
                    is_baby=specie_attributes.is_baby,
                    shape_url=specie_attributes.shape_url,
                    shape_name=specie_attributes.shape_name,
                    is_mythical=specie_attributes.is_mythical,
                    gender_rate=specie_attributes.gender_rate,
                    is_legendary=specie_attributes.is_legendary,
                    capture_rate=specie_attributes.capture_rate,
                    hatch_counter=specie_attributes.hatch_counter,
                    base_happiness=specie_attributes.base_happiness,
                    special_attack=pokemon_with_pokemon_name.special_attack,
                    base_experience=pokemon_with_pokemon_name.base_experience,
                    special_defense=pokemon_with_pokemon_name.special_defense,
                    evolution_chain_url=specie_attributes.evolution_chain_url,
                    evolves_from_species=specie_attributes.evolves_from_species,
                    has_gender_differences=specie_attributes.has_gender_differences,
                ),
                types=types,
                moves=moves,
                abilities=abilities,
            )

        except httpx.HTTPError as e:
            print(f'# => fetch_by_name => error => {e}')
            raise HTTPException(
                status_code=HTTPStatus.SERVICE_UNAVAILABLE,
                detail='Failed to execute external request:(fetch_by_name).',
            )
