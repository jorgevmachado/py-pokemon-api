import logging
from typing import Annotated

from fastapi import Depends

from app.core.exceptions.exceptions import handle_service_exception
from app.core.logging import LoggingParams, log_service_success
from app.core.service import BaseService
from app.domain.ability.repository import PokemonAbilityRepository
from app.domain.ability.schema import PokemonAbilitySchema
from app.domain.pokemon.external.schemas import (
    PokemonExternalBaseAbilitySchemaResponse,
)
from app.models.pokemon_ability import PokemonAbility
from app.shared.utils.number import ensure_order_number

Repository = Annotated[PokemonAbilityRepository, Depends()]
logger = logging.getLogger(__name__)


class PokemonAbilityService(BaseService[Repository, PokemonAbility]):
    def __init__(self, repository: Repository):
        logger_params = LoggingParams(
            logger=logger, service='ability', operation='verify_pokemon_abilities'
        )
        super().__init__('ability', repository, logger_params, PokemonAbilitySchema)

    async def verify_pokemon_abilities(
        self, abilities: list[PokemonExternalBaseAbilitySchemaResponse]
    ) -> list[PokemonAbility]:
        try:
            result_pokemon_abilities = []
            for ability_response in abilities:
                url = ability_response.ability.url
                name = ability_response.ability.name
                order = ensure_order_number(url)

                db_pokemon_ability = await self.repository.find_by(order=order)
                if db_pokemon_ability:
                    result_pokemon_abilities.append(db_pokemon_ability)
                    continue

                pokemon_ability = await self.repository.save(
                    PokemonAbility(
                        name=name,
                        url=url,
                        order=order,
                        slot=ability_response.slot,
                        is_hidden=ability_response.is_hidden,
                    )
                )
                result_pokemon_abilities.append(pokemon_ability)
            log_service_success(
                self.logger_params, message='Verify Pokemon Abilities successfully'
            )
            return result_pokemon_abilities
        except Exception as exception:
            handle_service_exception(
                exception,
                logger=self.logger_params.logger,
                service=self.logger_params.service,
                operation=self.logger_params.operation,
                raise_exception=False,
            )
            return []
