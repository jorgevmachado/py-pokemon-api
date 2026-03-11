import logging
from typing import Annotated

from fastapi import Depends

from app.domain.ability.model import PokemonAbility
from app.domain.ability.repository import PokemonAbilityRepository
from app.domain.ability.schema import CreatePokemonAbilitySchema
from app.domain.pokemon.external.schemas import (
    PokemonExternalBaseAbilitySchemaResponse,
)
from app.shared.exceptions import handle_service_exception
from app.shared.number import ensure_order_number

Repository = Annotated[PokemonAbilityRepository, Depends()]
logger = logging.getLogger(__name__)


class PokemonAbilityService:
    def __init__(self, repository: Repository):
        self.repository = repository

    async def verify_pokemon_abilities(
        self, abilities: list[PokemonExternalBaseAbilitySchemaResponse]
    ) -> list[PokemonAbility]:
        try:
            result_pokemon_abilities = []
            for ability_response in abilities:
                url = ability_response.ability.url
                name = ability_response.ability.name
                order = ensure_order_number(url)

                db_pokemon_ability = await self.repository.find_one_by_order(order=order)
                if db_pokemon_ability:
                    result_pokemon_abilities.append(db_pokemon_ability)
                    continue

                pokemon_ability_data = CreatePokemonAbilitySchema(
                    url=url,
                    name=name,
                    order=order,
                    slot=ability_response.slot,
                    is_hidden=ability_response.is_hidden,
                )
                pokemon_ability = await self.repository.create(pokemon_ability_data)
                result_pokemon_abilities.append(pokemon_ability)

            return result_pokemon_abilities
        except Exception as exception:
            handle_service_exception(
                exception,
                logger=logger,
                service='ability',
                operation='verify_pokemon_abilities',
                raise_exception=False,
            )
            return []
