from typing import Annotated

from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.domain.pokemon.external.service import PokemonExternalService
from app.domain.pokemon.repository import PokemonRepository
from app.domain.pokemon.schema import CreatePokemonSchema
from app.models import Pokemon
from app.shared.schemas import FilterPage

POKEMON_TOTAL_LIMIT = 1302
Session = Annotated[AsyncSession, Depends(get_session)]


class PokemonService:
    def __init__(self, session: Session):
        self.repository = PokemonRepository(session)
        self.external_service = PokemonExternalService()

    async def fetch_all(self, pokemon_filter: Annotated[FilterPage, Query()]):
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
