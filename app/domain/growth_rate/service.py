import logging
from typing import Annotated, Optional

from fastapi import Depends

from app.core.logging import LoggingParams, log_service_success
from app.domain.growth_rate.business import PokemonGrowthRateBusiness
from app.domain.growth_rate.model import PokemonGrowthRate
from app.domain.growth_rate.repository import PokemonGrowthRateRepository
from app.domain.growth_rate.schema import CreatePokemonGrowthRateSchema
from app.domain.pokemon.external.schemas import (
    PokemonExternalBase,
)
from app.domain.pokemon.external.service import PokemonExternalService
from app.shared.exceptions import handle_service_exception
from app.shared.number import ensure_order_number

Repository = Annotated[PokemonGrowthRateRepository, Depends()]
logger = logging.getLogger(__name__)


class PokemonGrowthRateService:
    def __init__(self, repository: Repository):
        self.repository = repository
        self.external_service = PokemonExternalService()
        self.logger_params = LoggingParams(
            logger=logger, service='growth_rate', operation='verify_pokemon_growth_rate'
        )

    async def verify_pokemon_growth_rate(
        self, growth_rate: Optional[PokemonExternalBase] = None
    ) -> PokemonGrowthRate | None:
        if not growth_rate:
            return None
        try:
            url = growth_rate.url
            order = ensure_order_number(url)

            db_pokemon_growth_rate = await self.repository.find_by(order=order)
            if db_pokemon_growth_rate:
                log_service_success(
                    self.logger_params, message='Pokemon Growth Rate exist in database!'
                )
                return db_pokemon_growth_rate

            external_growth_rate_data = await (
                self.external_service.pokemon_external_growth_rate_by_order(order)
            )

            if not external_growth_rate_data:
                log_service_success(
                    self.logger_params,
                    message='External Service Pokemon Growth Rate not exists!',
                )
                return None

            description = PokemonGrowthRateBusiness().ensure_description_message(
                external_growth_rate_data.descriptions
            )

            log_service_success(self.logger_params, message='Pokemon Growth Rate create!')

            return await self.repository.save(
                entity=PokemonGrowthRate(
                    url=url,
                    name=external_growth_rate_data.name,
                    order=order,
                    formula=external_growth_rate_data.formula,
                    description=description,
                )
            )
        except Exception as exception:
            handle_service_exception(
                exception,
                logger=self.logger_params.logger,
                service=self.logger_params.service,
                operation='verify_pokemon_growth_rate',
                raise_exception=False,
            )
            return None
