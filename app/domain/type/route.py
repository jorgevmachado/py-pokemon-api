from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi_pagination import LimitOffsetPage

from app.core.security import get_current_user
from app.domain.ability.schema import PokemonAbilityFilterPage
from app.domain.pokemon.service import PokemonTypeService
from app.domain.type.schema import PokemonTypeSchema
from app.models.trainer import Trainer

router = APIRouter(prefix='/type', tags=['type'])
Service = Annotated[PokemonTypeService, Depends()]
CurrentTrainer = Annotated[Trainer, Depends(get_current_user)]


@router.get('/', response_model=LimitOffsetPage[PokemonTypeSchema] | list[PokemonTypeSchema])
async def list_type(
    service: Service,
    trainer: CurrentTrainer,
    page_filter: Annotated[PokemonAbilityFilterPage, Depends()] = None,
):
    return await service.list_all_cached(page_filter=page_filter, user_request=trainer.name)


@router.get('/{param}', response_model=PokemonTypeSchema)
async def find_one_type(
    param: str,
    service: Service,
    trainer: CurrentTrainer,
):
    return await service.find_one_cached(param=param, user_request=trainer.name)
