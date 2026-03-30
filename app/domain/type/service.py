import logging
from typing import Annotated

from fastapi import Depends

from app.core.exceptions import handle_service_exception
from app.core.logging import LoggingParams, log_service_success
from app.core.service import BaseService
from app.domain.pokemon.external.schemas import (
    PokemonExternalBase,
    PokemonExternalBaseTypeSchemaResponse,
)
from app.domain.pokemon.external.service import PokemonExternalService
from app.domain.type.business import PokemonTypeBusiness
from app.domain.type.repository import PokemonTypeRepository
from app.models.pokemon_type import PokemonType
from app.shared.utils.number import ensure_order_number

Repository = Annotated[PokemonTypeRepository, Depends()]
logger = logging.getLogger(__name__)


class PokemonTypeService(BaseService[Repository, PokemonType]):
    alias = 'Pokemon Type'

    def __init__(self, repository: Repository):
        self.external_service = PokemonExternalService()
        logger_params = LoggingParams(
            logger=logger, service='type', operation='verify_pokemon_type'
        )
        super().__init__(repository, logger_params)

    async def verify_pokemon_type(
        self, types: list[PokemonExternalBaseTypeSchemaResponse]
    ) -> list[PokemonType]:
        result: list[PokemonType] = []
        try:
            for type_response in types:
                url = type_response.type.url
                order = ensure_order_number(url)

                db_pokemon_type = await self.repository.find_by(order=order)
                if db_pokemon_type:
                    db_pokemon_type_with_relations = await self.add_relations(
                        pokemon_type=db_pokemon_type
                    )
                    result.append(db_pokemon_type_with_relations)
                    continue

                pokemon_type = await self.save(
                    create=PokemonExternalBase(
                        url=url,
                        name=type_response.type.name,
                    )
                )
                db_pokemon_type_with_relations = await self.add_relations(
                    pokemon_type=pokemon_type
                )
                result.append(db_pokemon_type_with_relations)
        except Exception as exception:
            handle_service_exception(
                exception,
                logger=self.logger_params.logger,
                service=self.logger_params.service,
                operation=self.logger_params.operation,
                raise_exception=False,
            )
        finally:
            log_service_success(
                self.logger_params,
                operation=self.logger_params.operation,
                message='Verify Pokemon Type successfully',
            )
            return result

    async def add_relations(self, pokemon_type: PokemonType) -> PokemonType:
        if not pokemon_type.weaknesses or not pokemon_type.strengths:
            pokemon_type_external = await self.external_service.pokemon_external_type(
                url=pokemon_type.url
            )
            pokemon_type_damage_relations = PokemonTypeBusiness().ensure_damage_relations(
                damage_relations=pokemon_type_external.damage_relations
            )

            weaknesses: list[PokemonType] = await self.persist_relations(
                relations=pokemon_type_damage_relations.weakness
            )
            strengths: list[PokemonType] = await self.persist_relations(
                relations=pokemon_type_damage_relations.strengths
            )

            if weaknesses or strengths:
                pokemon_type.weaknesses = weaknesses
                pokemon_type.strengths = strengths
                return await self.repository.update(pokemon_type)

            return pokemon_type
        return pokemon_type

    async def persist_relations(
        self, relations: list[PokemonExternalBase]
    ) -> list[PokemonType]:
        result: list[PokemonType] = []
        for relation in relations:
            entity = await self.save(create=relation)
            if entity:
                result.append(entity)
        return result

    async def save(self, create: PokemonExternalBase) -> PokemonType | None:
        url = create.url
        name = create.name
        order = ensure_order_number(create.url)

        db_pokemon_type = await self.repository.find_by(order=order)
        if db_pokemon_type:
            return db_pokemon_type

        type_colors = PokemonTypeBusiness().ensure_colors(create.name)
        return await self.repository.save(
            entity=PokemonType(
                url=url,
                name=name,
                order=order,
                text_color=type_colors.text_color,
                background_color=type_colors.background_color,
            )
        )
