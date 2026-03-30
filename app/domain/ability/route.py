from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi_pagination import LimitOffsetPage

from app.core.security import get_current_user
from app.domain.ability.schema import PokemonAbilityFilterPage, PokemonAbilitySchema
from app.domain.ability.service import PokemonAbilityService
from app.models.trainer import Trainer

router = APIRouter(prefix='/ability', tags=['ability'])
Service = Annotated[PokemonAbilityService, Depends()]
CurrentTrainer = Annotated[Trainer, Depends(get_current_user)]


@router.get(
    '/', response_model=LimitOffsetPage[PokemonAbilitySchema] | list[PokemonAbilitySchema]
)
async def list_abilities(
    service: Service,
    trainer: CurrentTrainer,
    page_filter: Annotated[PokemonAbilityFilterPage, Depends()] = None,
):
    return await service.list_all_cached(page_filter=page_filter, user_request=trainer.name)


@router.get('/{param}', response_model=PokemonAbilitySchema)
async def find_one_ability(
    param: str,
    service: Service,
    trainer: CurrentTrainer,
):
    return await service.find_one_cached(param=param, user_request=trainer.name)
