from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi_pagination import LimitOffsetPage

from app.core.security import get_current_user
from app.domain.pokedex.schema import PokedexDiscover, PokedexFilterPage, PokedexPublicSchema
from app.domain.pokedex.service import PokedexService
from app.models.trainer import Trainer

router = APIRouter(prefix='/pokedex', tags=['pokedex'])
Service = Annotated[PokedexService, Depends()]
CurrentTrainer = Annotated[Trainer, Depends(get_current_user)]


@router.get(
    '/',
    response_model=LimitOffsetPage[PokedexPublicSchema] | list[PokedexPublicSchema],
)
async def get_pokedex(
    service: Service,
    trainer: CurrentTrainer,
    page_filter: Annotated[PokedexFilterPage, Depends()],
):
    return await service.fetch_all(trainer_id=trainer.id, page_filter=page_filter)


@router.post('/discover', response_model=PokedexPublicSchema)
async def discover_pokemon(
    service: Service, trainer: CurrentTrainer, discover: PokedexDiscover
):
    return await service.discover(trainer_id=trainer.id, pokemon_name=discover.pokemon_name)
