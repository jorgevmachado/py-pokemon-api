from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.pagination import CustomLimitOffsetPage
from app.core.security import get_current_user
from app.domain.growth_rate.schema import PokemonGrowthRateSchema
from app.domain.growth_rate.service import PokemonGrowthRateService
from app.models.trainer import Trainer
from app.shared.schemas import FilterPage

router = APIRouter(prefix='/growth-rate', tags=['growth-rate'])
Service = Annotated[PokemonGrowthRateService, Depends()]
CurrentTrainer = Annotated[Trainer, Depends(get_current_user)]


@router.get(
    '/',
    response_model=CustomLimitOffsetPage[PokemonGrowthRateSchema]
    | list[PokemonGrowthRateSchema],
)
async def list_growth_rates(
    service: Service, page_filter: Annotated[FilterPage, Depends()], trainer: CurrentTrainer
):
    return await service.list_all_cached(page_filter=page_filter, user_request=trainer.name)


@router.get('/{param}', response_model=PokemonGrowthRateSchema)
async def find_one_growth_rate(param: str, service: Service, trainer: CurrentTrainer):
    return await service.find_one_cached(param=param, user_request=trainer.name)
