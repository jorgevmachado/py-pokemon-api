from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi_pagination import LimitOffsetPage

from app.core.security import get_current_user
from app.domain.captured_pokemon.schema import (
    CapturedPokemonPublicSchema,
    CapturePokemonHealSchema,
    CapturePokemonSchema,
)
from app.domain.captured_pokemon.service import CapturedPokemonService
from app.models.trainer import Trainer
from app.shared.schemas import FilterPage

router = APIRouter(prefix='/captured-pokemons', tags=['captured-pokemons'])
Service = Annotated[CapturedPokemonService, Depends()]
CurrentTrainer = Annotated[Trainer, Depends(get_current_user)]


@router.get(
    '/',
    response_model=LimitOffsetPage[CapturedPokemonPublicSchema]
    | list[CapturedPokemonPublicSchema],
)
async def get_captured_pokemons(
    service: Service,
    trainer: CurrentTrainer,
    page_filter: Annotated[FilterPage, Depends()],
):
    return await service.fetch_all(trainer_id=trainer.id, page_filter=page_filter)


@router.post('/capture', response_model=CapturedPokemonPublicSchema)
async def capture_pokemon(
    service: Service,
    trainer: CurrentTrainer,
    capture: CapturePokemonSchema,
):
    return await service.capture(trainer=trainer, capture_pokemon=capture)


@router.post('/heal', response_model=list[CapturedPokemonPublicSchema])
async def heal_pokemon(
    service: Service,
    trainer: CurrentTrainer,
    heal_pokemons: CapturePokemonHealSchema,
):
    return await service.heal(trainer_id=trainer.id, heal_pokemons=heal_pokemons)
