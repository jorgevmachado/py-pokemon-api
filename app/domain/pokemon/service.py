from http import HTTPStatus
from typing import Annotated

from fastapi import Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.domain.pokemon.ability.service import PokemonAbilityService
from app.domain.pokemon.external.service import PokemonExternalService
from app.domain.pokemon.growth_rate.service import PokemonGrowthRateService
from app.domain.pokemon.move.service import PokemonMoveService
from app.domain.pokemon.repository import PokemonRepository
from app.domain.pokemon.schema import CreatePokemonSchema, PokemonSchema
from app.domain.pokemon.type.service import PokemonTypeService
from app.models import Pokemon
from app.shared.number import ensure_order_number
from app.shared.schemas import FilterPage
from app.shared.status_enum import StatusEnum

POKEMON_TOTAL_LIMIT = 1302
Session = Annotated[AsyncSession, Depends(get_session)]


class PokemonService:
    def __init__(self, session: Session):
        self.repository = PokemonRepository(session)
        self.pokemon_move_service = PokemonMoveService(session)
        self.pokemon_type_service = PokemonTypeService(session)
        self.pokemon_ability_service = PokemonAbilityService(session)
        self.pokemon_growth_rate_service = PokemonGrowthRateService(session)
        self.external_service = PokemonExternalService()

    async def fetch_all(self, pokemon_filter: Annotated[FilterPage, Query()]) -> list[Pokemon]:
        try:
            total = await self.repository.total()
            if total != POKEMON_TOTAL_LIMIT:
                await self.initialize_database(total=total)

            pokemons = await self.repository.list(pokemon_filter=pokemon_filter)
            return pokemons

        except Exception as e:
            print(f'# => service => fetch_all => error => {e}')
        return []

    async def initialize_database(self, total: int = 0) -> list[Pokemon]:
        try:
            external_data = await self.external_service.pokemon_external_list(
                offset=0,
                limit=POKEMON_TOTAL_LIMIT,
            )

            if total == 0:
                result_initial = []
                for pokemon in external_data:
                    pokemon_to_create = CreatePokemonSchema(
                        name=pokemon.name,
                        order=pokemon.order,
                        url=pokemon.url,
                        external_image=pokemon.external_image,
                    )
                    pokemon_created = await self.repository.create(
                        pokemon_data=pokemon_to_create
                    )
                    result_initial.append(pokemon_created)
                return result_initial

            entities = await self.repository.list()

            existing_names = {entity.name for entity in entities}
            save_list = [item for item in external_data if item.name not in existing_names]
            result_final = []
            for pokemon_data in save_list:
                pokemon_to_add = CreatePokemonSchema(
                    name=pokemon_data.name,
                    order=pokemon_data.order,
                    url=pokemon_data.url,
                    external_image=pokemon_data.external_image,
                )
                pokemon_added = await self.repository.create(pokemon_data=pokemon_to_add)
                result_final.append(pokemon_added)
            return result_final

        except Exception as e:
            print(f'# => service => initialize_database => error => {e}')
            return []

    async def fetch_one(self, name: str) -> Pokemon | None:
        return await self.validate_entity(name)

    async def validate_entity(
        self,
        pokemon_name: str,
    ) -> Pokemon:
        pokemon = await self.repository.find_one(name=pokemon_name)

        if not pokemon:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Pokemon not found')

        if pokemon.status == StatusEnum.INCOMPLETE:
            return await self.complete_pokemon_data(pokemon=pokemon)

        return pokemon

    async def complete_pokemon_data(self, pokemon: Pokemon) -> Pokemon:
        external_data = await self.external_service.fetch_by_name(
            pokemon=PokemonSchema.model_validate(pokemon)
        )
        moves = await self.pokemon_move_service.verify_pokemon_move(external_data.moves)
        print(f'# => service => complete_pokemon_data => moves => {moves}')
        types = await self.pokemon_type_service.verify_pokemon_type(external_data.types)
        print(f'# => service => complete_pokemon_data => types => {types}')
        abilities = await self.pokemon_ability_service.verify_pokemon_abilities(
            external_data.abilities
        )
        print(f'# => service => complete_pokemon_data => abilities => {abilities}')
        growth_rate = await self.pokemon_growth_rate_service.verify_pokemon_growth_rate(
            external_data.growth_rate
        )
        print(f'# => service => complete_pokemon_data => growth_rate => {growth_rate}')
        await self.repository.update(pokemon)
        evolutions = await self.complete_evolution(
            external_data.pokemon.evolution_chain_url
        )
        print(f'# => service => complete_pokemon_data => evolutions => {evolutions}')
        return await self.repository.find_one(name=pokemon.name)

    async def complete_evolution(
            self,
            evolution_chain_url: str | None,
    ) -> list[Pokemon]:
        if not evolution_chain_url:
            return []

        order = ensure_order_number(evolution_chain_url)

        if order == 0:
            return []

        return []
