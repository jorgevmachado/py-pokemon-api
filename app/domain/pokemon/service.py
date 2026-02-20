from http import HTTPStatus
from os import name
from typing import Annotated

from fastapi import Depends, Query, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.domain.pokemon.ability.service import PokemonAbilityService
from app.domain.pokemon.external.service import PokemonExternalService
from app.domain.pokemon.growth_rate.service import PokemonGrowthRateService
from app.domain.pokemon.move.service import PokemonMoveService
from app.domain.pokemon.repository import PokemonRepository
from app.domain.pokemon.schema import PokemonPublicSchema
from app.domain.pokemon.type.service import PokemonTypeService
from app.models import Pokemon
from app.shared.schemas import FilterPage
from app.shared.status_enum import StatusEnum

Session = Annotated[AsyncSession, Depends(get_session)]
POKEMON_TOTAL_LIMIT = 1302

class PokemonService:
    def __init__(self, session: Session):
        self.external_service = PokemonExternalService()
        self.repository = PokemonRepository(session)
        self.pokemon_type_service = PokemonTypeService(session)
        self.pokemon_move_service = PokemonMoveService(session)
        self.pokemon_growth_rate_service = PokemonGrowthRateService(session)
        self.pokemon_ability_service = PokemonAbilityService(session)

    async def validate_database(self, pokemon_filter: Annotated[FilterPage, Query()]):
        try:
            total = await self.repository.total()
            if total != POKEMON_TOTAL_LIMIT:
                await PokemonService.initialize_database(self, total=total)

            pokemons = await self.repository.list(pokemon_filter)
            return pokemons
        except Exception as e:
            print(f'# => validate_database => error => {e}')
            return []

    async def initialize_database(self, total: int = 0):
        try:
            external_data = await self.external_service.fetch(
                offset=0,
                limit=POKEMON_TOTAL_LIMIT,
            )
            if total == 0:
                for pokemon_data in external_data:
                    await self.repository.create(pokemon_data)
                return
            entities = await self.repository.list()

            existing_names = {entity.name for entity in entities}
            save_list = [
                item for item in external_data
                if item['name'] not in existing_names
            ]
            for pokemon_data in save_list:
                await self.repository.create(pokemon_data)

            print('# => external_data => ', external_data)
        except Exception as e:
            print(f'# => initialize_database => error => {e}')

    async def find_one(self, name: str):
        pokemon = await self.repository.find_one(name)
        if not pokemon:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, detail='Pokemon not found'
            )
        if pokemon.status == StatusEnum.INCOMPLETE:
            return await PokemonService.completingPokemonData(self, pokemon)
        return pokemon

    async def completingPokemonData(self, data: PokemonPublicSchema):
        external_data = await self.external_service.fetch_name(data)
        types = self.pokemon_type_service.convert_types_to_pokemon_types(external_data.types)

        print('# => types => ', types)
        return external_data.pokemon