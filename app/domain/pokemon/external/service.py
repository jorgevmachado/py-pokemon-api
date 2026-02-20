from http import HTTPStatus

import httpx
from typing import Annotated

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.domain.pokemon.external.schema import PokemonByNameSchema, PokemonSpecieSchema, PokemonSpritesSchema, \
    FetchNameResultSchema, PokemonBaseResponse
from app.domain.pokemon.schema import PokemonPublicSchema
from app.shared.number import ensure_order_number
from app.shared.status_enum import StatusEnum

Session = Annotated[AsyncSession, Depends(get_session)]


class PokemonExternalService:
    BASE_URL = 'https://pokeapi.co/api/v2'

    @staticmethod
    async def fetch(offset: int, limit: int):
        try:
            async with httpx.AsyncClient(verify=False) as client:
                response = await client.get(
                    f'{PokemonExternalService.BASE_URL}/pokemon',
                    params={'limit': limit, 'offset': offset},
                    timeout=10.0,
                )
                response.raise_for_status()
                if response and 'results' in response.json():
                    results = response.json()['results']
                    new_results = [
                        {**item, 'order': ensure_order_number(item.get('url'))}
                        for item in results
                    ]
                    return new_results
                raise HTTPException(
                    status_code=HTTPStatus.SERVICE_UNAVAILABLE, detail='Failed to execute external request:(list).'
                )
        except httpx.HTTPError as e:
            print(f'# => fetch => error => {e}')
            raise HTTPException(
                status_code=HTTPStatus.SERVICE_UNAVAILABLE, detail='Failed to execute external request:(list).'
            )

    @staticmethod
    async def get_by_name(name: str):
        try:
            async with httpx.AsyncClient(verify=False) as client:
                response = await client.get(
                    f'{PokemonExternalService.BASE_URL}/pokemon/{name}',
                    timeout=10.0,
                )
                response.raise_for_status()
                if response and 'name' in response.json():
                    return PokemonByNameSchema(**response.json())
                return None
        except httpx.HTTPError as e:
            print(f'# => get_by_name => error => {e}')
            raise HTTPException(
                status_code=HTTPStatus.SERVICE_UNAVAILABLE, detail='Failed to execute external request:(name).'
            )

    @staticmethod
    async def get_specie_by_name(name: str):
        try:
            async with httpx.AsyncClient(verify=False) as client:
                response = await client.get(
                    f'{PokemonExternalService.BASE_URL}/pokemon-species/{name}',
                    timeout=10.0,
                )
                response.raise_for_status()
                if response and 'name' in response.json():
                    return PokemonSpecieSchema(**response.json())
                return None
        except httpx.HTTPError as e:
            print(f'# => get_specie_by_name => error => {e}')
            raise HTTPException(
                status_code=HTTPStatus.SERVICE_UNAVAILABLE, detail='Failed to execute external request:(specie).'
            )


    @staticmethod
    async def fetch_name(pokemon: PokemonPublicSchema) -> FetchNameResultSchema:
        try:
            pokemon_dict = pokemon.__dict__ if hasattr(pokemon, '__dict__') and not isinstance(pokemon,dict) else pokemon
            current_pokemon = PokemonPublicSchema(**pokemon_dict)
            current_pokemon.status = StatusEnum.INCOMPLETE
            pokemon_name = await PokemonExternalService.get_by_name(name=current_pokemon.name)
            if not pokemon_name:
                return FetchNameResultSchema(
                    status=StatusEnum.INCOMPLETE,
                    pokemon=current_pokemon,
                    types=[],
                    moves=[],
                    abilities=[],
                    growth_rate=None
                )
            current_pokemon.height = pokemon_name.height if pokemon_name.height else 0
            current_pokemon.weight = pokemon_name.weight if pokemon_name.weight else 0
            current_pokemon.base_experience = pokemon_name.base_experience if pokemon_name.base_experience else 0
            current_pokemon.image = PokemonExternalService.ensure_image(pokemon_name.sprites)
            for stat in pokemon_name.stats:
                if stat.stat.name == 'hp':
                    current_pokemon.hp = stat.base_stat
                if stat.stat.name == 'speed':
                    current_pokemon.speed = stat.base_stat
                if stat.stat.name == 'attack':
                    current_pokemon.attack = stat.base_stat
                if stat.stat.name == 'defense':
                    current_pokemon.defense = stat.base_stat
                if stat.stat.name == 'special-attack':
                    current_pokemon.special_attack = stat.base_stat
                if stat.stat.name == 'special-defense':
                    current_pokemon.special_defense = stat.base_stat

            pokemon_specie = await PokemonExternalService.get_specie_by_name(name=current_pokemon.name)
            if not pokemon_specie:
                return FetchNameResultSchema(
                    status=StatusEnum.INCOMPLETE,
                    pokemon=current_pokemon,
                    types=pokemon_name.types,
                    moves=pokemon_name.moves,
                    abilities=pokemon_name.abilities,
                    growth_rate=None
                )


            if pokemon_specie.habitat:
                current_pokemon.habitat = pokemon_specie.habitat.name

            current_pokemon.is_baby = pokemon_specie.is_baby

            if pokemon_specie.shape:
                current_pokemon.shape_name = pokemon_specie.shape.name
                current_pokemon.shape_url = pokemon_specie.shape.url

            current_pokemon.is_mythical = pokemon_specie.is_mythical
            current_pokemon.gender_rate = pokemon_specie.gender_rate
            current_pokemon.is_legendary = pokemon_specie.is_legendary
            current_pokemon.capture_rate = pokemon_specie.capture_rate
            current_pokemon.hatch_counter = pokemon_specie.hatch_counter
            current_pokemon.base_happiness = pokemon_specie.base_happiness

            if pokemon_specie.evolution_chain:
                current_pokemon.evolution_chain_url = pokemon_specie.evolution_chain.url

            if pokemon_specie.evolves_from_species:
                current_pokemon.evolves_from_species = pokemon_specie.evolves_from_species

            current_pokemon.has_gender_differences = pokemon_specie.has_gender_differences
            current_pokemon.status = StatusEnum.COMPLETE

            return FetchNameResultSchema(
                status=StatusEnum.COMPLETE,
                pokemon=current_pokemon,
                types=pokemon_name.types,
                moves=pokemon_name.moves,
                abilities=pokemon_name.abilities,
                growth_rate=PokemonBaseResponse(
                    name=pokemon_specie.growth_rate.name,
                    url=pokemon_specie.growth_rate.url
                )
            )

        except httpx.HTTPError as e:
            print(f'# => fetch_name => error => {e}')
            raise HTTPException(
                status_code=HTTPStatus.SERVICE_UNAVAILABLE, detail='Failed to execute external request:(specie).'
            )

    @staticmethod
    def ensure_image(sprites: PokemonSpritesSchema | None):
        if not sprites:
            return ''

        front_default = sprites.front_default
        dream_world = sprites.other.dream_world.front_default
        return front_default if front_default else dream_world

    @staticmethod
    def ensure_statistics_attributes(stats: PokemonByNameSchema):
        stat_mapping = {
            'hp': 'hp',
            'speed': 'speed',
            'attack': 'attack',
            'defense': 'defense',
            'special-attack': 'special_attack',
            'special-defense': 'special_defense',
        }

        result = {
            'hp': 0,
            'speed': 0,
            'attack': 0,
            'defense': 0,
            'special_attack': 0,
            'special_defense': 0,
        }

        for stat in stats:
            stat_name = stat.get('stat', {}).get('name')
            if stat_name in stat_mapping:
                result[stat_mapping[stat_name]] = stat.get('base_stat', 0)

        return result