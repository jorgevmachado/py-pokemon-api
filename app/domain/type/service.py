import logging
from typing import Annotated

from fastapi import Depends

from app.domain.pokemon.external.schemas import (
    PokemonExternalBase,
    PokemonExternalBaseTypeSchemaResponse,
)
from app.domain.pokemon.external.service import PokemonExternalService
from app.domain.type.business import PokemonTypeBusiness
from app.domain.type.model import PokemonType
from app.domain.type.repository import PokemonTypeRepository
from app.domain.type.schema import (
    CreatePokemonTypeSchema,
    ValidatePokemonTypeDamageRelationSchema,
)
from app.shared.exceptions import log_service_exception
from app.shared.number import ensure_order_number

Repository = Annotated[PokemonTypeRepository, Depends()]
logger = logging.getLogger(__name__)


class PokemonTypeService:
    def __init__(self, repository: Repository):
        self.repository = repository
        self.external_service = PokemonExternalService()

    async def verify_pokemon_type(
        self, types: list[PokemonExternalBaseTypeSchemaResponse]
    ) -> list[PokemonType]:
        try:
            result_pokemon_type = []
            for type_response in types:
                url = type_response.type.url
                order = ensure_order_number(url)

                db_pokemon_type = await self.repository.find_one_by_order(order=order)
                if db_pokemon_type:
                    result_pokemon_type.append(db_pokemon_type)
                    continue
                pokemon_type = await self.persist(pokemon_type=type_response.type)
                result_pokemon_type.append(pokemon_type)

            return result_pokemon_type
        except Exception as exception:
            log_service_exception(
                exception,
                logger=logger,
                service='type',
                operation='verify_pokemon_type',
            )
            return []

    async def validate_damage_relations(
        self, url: str
    ) -> ValidatePokemonTypeDamageRelationSchema:
        weakness = []
        strengths = []
        external_type_data = await self.external_service.pokemon_external_type_by_url(url=url)

        if external_type_data is not None:
            pokemon_type_damage_relations = PokemonTypeBusiness().ensure_damage_relations(
                damage_relations=external_type_data.damage_relations
            )
            weakness = await self.persist_damage_relations(
                pokemon_type_damage_relations.weakness
            )
            strengths = await self.persist_damage_relations(
                pokemon_type_damage_relations.strengths
            )

        return ValidatePokemonTypeDamageRelationSchema(
            weaknesses=weakness,
            strengths=strengths,
        )

    async def persist_damage_relations(
        self,
        damage_relations: list[PokemonExternalBase],
    ) -> list[PokemonType]:
        result = []
        for damage_relation in damage_relations:
            damage = await self.persist(
                pokemon_type=damage_relation,
                with_damage_relations=False,
            )
            result.append(damage)
        return result

    async def persist(
        self,
        pokemon_type: PokemonExternalBase,
        with_damage_relations: bool = True,
    ) -> PokemonType:
        url = pokemon_type.url
        order = ensure_order_number(url)

        existing_type = await self.repository.find_one_by_order(order=order)
        if not existing_type:
            existing_type = await self.repository.find_one(name=pokemon_type.name)

        if existing_type:
            if (
                with_damage_relations
                and not existing_type.weaknesses
                and not existing_type.strengths
            ):
                damages = await self.validate_damage_relations(url=url)
                if damages.weaknesses:
                    existing_type.weaknesses = damages.weaknesses
                if damages.strengths:
                    existing_type.strengths = damages.strengths
                return await self.repository.update(existing_type)

            return existing_type

        type_colors = PokemonTypeBusiness().ensure_colors(pokemon_type.name)
        pokemon_type_data = CreatePokemonTypeSchema(
            url=url,
            name=pokemon_type.name,
            order=order,
            text_color=type_colors.text_color,
            background_color=type_colors.background_color,
        )

        return await self.repository.create(pokemon_type_data)
