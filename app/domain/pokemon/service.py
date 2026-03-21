import logging
from http import HTTPStatus
from typing import Annotated

from fastapi import Depends, HTTPException, Query

from app.core.logging import LoggingParams, log_service_success
from app.domain.ability.service import PokemonAbilityService
from app.domain.growth_rate.service import PokemonGrowthRateService
from app.domain.move.service import PokemonMoveService
from app.domain.pokemon.business import PokemonBusiness
from app.domain.pokemon.cache import PokemonCacheService
from app.domain.pokemon.external.service import PokemonExternalService
from app.domain.pokemon.model import Pokemon
from app.domain.pokemon.repository import PokemonRepository
from app.domain.pokemon.schema import (
    FirstPokemonSchemaResult,
    GeneratePokemonRelationshipSchema,
    GeneratePokemonRelationshipSchemaResult,
    PokemonFilterPage,
    PokemonSchema,
)
from app.domain.type.service import PokemonTypeService
from app.shared.enums.status_enum import StatusEnum
from app.shared.exceptions import handle_service_exception
from app.shared.schemas import FilterPage
from app.shared.utils.pagination import exception_pagination

POKEMON_TOTAL_LIMIT = 1302
Repository = Annotated[PokemonRepository, Depends()]
PokemonMoveService = Annotated[PokemonMoveService, Depends()]
PokemonTypeService = Annotated[PokemonTypeService, Depends()]
PokemonAbilityService = Annotated[PokemonAbilityService, Depends()]
PokemonGrowthRateService = Annotated[PokemonGrowthRateService, Depends()]
logger = logging.getLogger(__name__)


class PokemonService:
    def __init__(
        self,
        repository: Repository,
        pokemon_move_service: PokemonMoveService,
        pokemon_type_service: PokemonTypeService,
        pokemon_ability_service: PokemonAbilityService,
        pokemon_growth_rate_service: PokemonGrowthRateService,
    ):
        self.repository = repository
        self.pokemon_move_service = pokemon_move_service
        self.pokemon_type_service = pokemon_type_service
        self.pokemon_ability_service = pokemon_ability_service
        self.pokemon_growth_rate_service = pokemon_growth_rate_service
        self.external_service = PokemonExternalService()
        self.business = PokemonBusiness()
        self.logger_params = LoggingParams(logger=logger, service='pokemon', operation='')
        self.pokemon_cache_service = PokemonCacheService(logger_params=self.logger_params)

    async def total(self) -> int:
        log_service_success(
            self.logger_params, operation='total', message='Total Pokémon successfully'
        )
        return await self.repository.total()

    async def list_sync(self) -> None:
        cached_meta = await self.pokemon_cache_service.get_meta()
        if cached_meta:
            return None
        db_total = await self.repository.total()
        external_total = await self.external_service.pokemon_external_total()
        await self.pokemon_cache_service.set_meta(
            db_total=db_total, external_total=external_total
        )

        if db_total == 0:
            await self.initialize_database(
                total=0,
                external_total=external_total,
            )
            return None

        if external_total > db_total:
            await self.initialize_database(
                total=external_total,
                external_total=external_total,
            )
            new_db_total = await self.repository.total()
            await self.pokemon_cache_service.set_meta(
                db_total=new_db_total, external_total=external_total
            )
            return None

        return None

    async def list_all(
        self,
        page_filter: Annotated[PokemonFilterPage, Query()] = None,
    ):
        try:
            await self.list_sync()
            return await self.repository.list_all(page_filter=page_filter)

        except Exception as exception:
            handle_service_exception(
                exception,
                logger=self.logger_params.logger,
                service=self.logger_params.service,
                operation='list_all',
                raise_exception=False,
            )
        return exception_pagination(page_filter)

    async def list_all_cached(
        self,
        page_filter: Annotated[PokemonFilterPage, Query()] = None,
    ):
        key = self.pokemon_cache_service.build_key_all(page_filter=page_filter)

        cached = await self.pokemon_cache_service.get_all(key)
        if cached:
            return cached
        list_pokemons = await self.list_all(page_filter=page_filter)
        await self.pokemon_cache_service.set_all(key, list_pokemons)
        return list_pokemons

    async def initialize(
        self,
        page_filter: Annotated[FilterPage, Query()] = None,
    ):
        try:
            total = await self.repository.total()
            if total != POKEMON_TOTAL_LIMIT:
                await self.initialize_database(total=total)

            log_service_success(
                self.logger_params,
                operation='initialize',
                message='Initialize all Pokémon successfully',
            )
            return await self.repository.list_all(page_filter=page_filter)

        except Exception as exception:
            handle_service_exception(
                exception,
                logger=self.logger_params.logger,
                service=self.logger_params.service,
                operation='initialize',
                raise_exception=False,
            )
        return exception_pagination(page_filter)

    async def initialize_database(
        self,
        total: int = 0,
        external_total: int = POKEMON_TOTAL_LIMIT,
    ) -> list[Pokemon]:
        try:
            external_data = await self.external_service.pokemon_external_list(
                offset=0,
                limit=external_total,
            )

            if total == 0:
                result_initial = []
                for pokemon in external_data:
                    pokemon_to_create = Pokemon(
                        name=pokemon.name,
                        order=pokemon.order,
                        url=pokemon.url,
                        status=StatusEnum.INCOMPLETE,
                        external_image=pokemon.external_image,
                    )
                    pokemon_created = await self.repository.save(entity=pokemon_to_create)
                    result_initial.append(pokemon_created)
                    log_service_success(
                        self.logger_params,
                        operation='initialize_database',
                        message='Initialize all Pokémons from external in database!',
                    )
                return result_initial

            entities = await self.repository.list_all()

            existing_names = {entity.name for entity in entities}
            save_list = [item for item in external_data if item.name not in existing_names]
            result_final = []
            for pokemon_data in save_list:
                pokemon_to_add = Pokemon(
                    name=pokemon_data.name,
                    order=pokemon_data.order,
                    url=pokemon_data.url,
                    status=StatusEnum.INCOMPLETE,
                    external_image=pokemon_data.external_image,
                )
                pokemon_added = await self.repository.save(entity=pokemon_to_add)
                result_final.append(pokemon_added)

            log_service_success(
                self.logger_params,
                operation='initialize_database',
                message='Initialize some Pokémons from external in database successfully',
            )
            return result_final

        except Exception as exception:
            handle_service_exception(
                exception,
                logger=self.logger_params.logger,
                service=self.logger_params.service,
                operation='initialize_database',
                raise_exception=False,
            )
            return []

    async def fetch_one(self, name: str) -> Pokemon | None:
        log_service_success(
            self.logger_params,
            operation='initialize_database',
            message='Fetch One Pokémon successfully',
        )
        return await self.validate_entity(name)

    async def validate_entity(
        self,
        pokemon_name: str,
        with_evolutions: bool = True,
    ) -> Pokemon:
        pokemon = await self.repository.find_by(name=pokemon_name)

        if not pokemon:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Pokemon not found')

        if pokemon.status == StatusEnum.INCOMPLETE:
            log_service_success(
                self.logger_params,
                operation='validate_entity',
                message='Complete attributes from external service in database successfully',
            )
            return await self.complete_pokemon_data(
                pokemon=pokemon, with_evolutions=with_evolutions
            )

        log_service_success(
            self.logger_params,
            operation='validate_entity',
            message='Pokemon is complete in database',
        )
        return pokemon

    async def complete_pokemon_data(
        self,
        pokemon: Pokemon,
        with_evolutions: bool = True,
    ) -> Pokemon:
        try:
            external_data = await self.external_service.fetch_by_name(
                pokemon=PokemonSchema.model_validate(pokemon)
            )

            relationships = await self.generate_relationships(
                relationships=GeneratePokemonRelationshipSchema(
                    moves=external_data.moves,
                    types=external_data.types,
                    abilities=external_data.abilities,
                    growth_rate=external_data.growth_rate,
                )
            )
            pokemon.moves = relationships.moves
            pokemon.types = relationships.types
            pokemon.abilities = relationships.abilities
            pokemon.growth_rate = relationships.growth_rate
            pokemon.status = relationships.status

            if relationships.growth_rate is not None:
                pokemon.growth_rate_id = relationships.growth_rate.id

            if with_evolutions:
                evolutions = await self.add_evolutions(
                    external_data.pokemon.evolution_chain_url
                )
                pokemon.evolutions = evolutions

            pokemon_updated = self.business.merge_if_changed(
                pokemon_source=external_data.pokemon,
                pokemon_target=pokemon,
            )
            pokemon_updated.status = relationships.status

            await self.repository.update(pokemon_updated)
            log_service_success(
                self.logger_params,
                operation='complete_pokemon_data',
                message='Pokemon completed successfully',
            )
            return await self.repository.find_by(name=pokemon.name)
        except Exception as exception:
            handle_service_exception(
                exception,
                logger=self.logger_params.logger,
                service=self.logger_params.service,
                operation='complete_pokemon_data',
            )

    async def add_evolutions(
        self,
        evolution_chain_url: str | None,
    ) -> list[Pokemon]:
        evolutions: list[Pokemon] = []

        try:
            evolution_chain = await self.external_service.pokemon_external_evolution_by_url(
                evolution_chain_url
            )

            if not evolution_chain:
                log_service_success(
                    self.logger_params,
                    operation='add_evolutions',
                    message='Dont has evolutions for this Pokémon',
                )
                return evolutions

            evolutions_to_add = self.business.ensure_evolution(evolution_chain.chain)

            for evolution in evolutions_to_add:
                pokemon_evolution = await self.validate_entity(
                    evolution,
                    with_evolutions=False,
                )
                evolutions.append(pokemon_evolution)
            log_service_success(
                self.logger_params,
                operation='add_evolutions',
                message='Add evolutions successfully',
            )
            return evolutions
        except Exception as exception:
            handle_service_exception(
                exception,
                logger=self.logger_params.logger,
                service=self.logger_params.service,
                operation='add_evolutions',
                raise_exception=False,
            )
            return evolutions

    async def generate_relationships(
        self, relationships: GeneratePokemonRelationshipSchema
    ) -> GeneratePokemonRelationshipSchemaResult:
        moves = await self.pokemon_move_service.verify_pokemon_move(relationships.moves)
        types = await self.pokemon_type_service.verify_pokemon_type(relationships.types)
        abilities = await self.pokemon_ability_service.verify_pokemon_abilities(
            relationships.abilities
        )
        growth_rate = await self.pokemon_growth_rate_service.verify_pokemon_growth_rate(
            relationships.growth_rate
        )

        has_invalid_inputs = not moves or not types or not abilities

        status = StatusEnum.COMPLETE
        if has_invalid_inputs:
            status = StatusEnum.INCOMPLETE
        log_service_success(
            self.logger_params,
            operation='generate_relationships',
            message='Generate relationships successfully',
        )
        return GeneratePokemonRelationshipSchemaResult(
            status=status,
            moves=moves,
            types=types,
            abilities=abilities,
            growth_rate=growth_rate,
        )

    async def first_pokemon(self, name: str | None = None) -> FirstPokemonSchemaResult:
        try:
            pokemons_result = await self.list_all()

            pokemons = (
                list(pokemons_result.items)
                if hasattr(pokemons_result, 'items')
                else pokemons_result
            )

            first_pokemon = self.business.find_first_pokemon(
                pokemons=pokemons, pokemon_name=name
            )

            if not first_pokemon:
                log_service_success(
                    self.logger_params,
                    operation='first_pokemon',
                    message='Dont has first pokemon with this name',
                )
                return FirstPokemonSchemaResult(
                    pokemon=None,
                    pokemons=pokemons,
                )
            pokemon = await self.fetch_one(name=first_pokemon.name)
            log_service_success(
                self.logger_params,
                operation='first_pokemon',
                message='Return First Pokemon Successfully',
            )
            return FirstPokemonSchemaResult(
                pokemon=pokemon,
                pokemons=pokemons,
            )
        except Exception as exception:
            handle_service_exception(
                exception,
                logger=self.logger_params.logger,
                service=self.logger_params.service,
                operation='first_pokemon',
            )
