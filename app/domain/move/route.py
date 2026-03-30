from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi_pagination import LimitOffsetPage

from app.core.security import get_current_user
from app.domain.move.schema import PokemonMoveFilterPage, PokemonMoveSchema
from app.domain.move.service import PokemonMoveService
from app.models.trainer import Trainer

router = APIRouter(prefix='/move', tags=['move'])
Service = Annotated[PokemonMoveService, Depends()]
CurrentTrainer = Annotated[Trainer, Depends(get_current_user)]


@router.get('/', response_model=LimitOffsetPage[PokemonMoveSchema] | list[PokemonMoveSchema])
async def list_moves(
    service: Service,
    trainer: CurrentTrainer,
    page_filter: Annotated[PokemonMoveFilterPage, Depends()] = None,
):
    return await service.list_all(page_filter=page_filter, user_request=trainer.name)


@router.get('/{param}', response_model=PokemonMoveSchema)
async def find_one_move(
    param: str,
    service: Service,
    trainer: CurrentTrainer,
):
    return await service.find_one(param=param, user_request=trainer.name)
