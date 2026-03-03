from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi_pagination import LimitOffsetPage
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.security import get_current_user
from app.domain.captured_pokemon.schema import (
    CapturedPokemonFilterPage,
    CapturedPokemonPublicSchema,
    CapturePokemonSchema,
)
from app.domain.pokedex.schema import PokedexFilterPage, PokedexPublicSchema
from app.domain.trainer.model import Trainer
from app.domain.trainer.schema import (
    BattlePokemonSchema,
    CreateTrainerSchema,
    TrainerPublicSchema,
)
from app.domain.trainer.service import TrainerService

router = APIRouter(prefix='/trainers', tags=['trainers'])
Session = Annotated[AsyncSession, Depends(get_session)]
CurrentTrainer = Annotated[Trainer, Depends(get_current_user)]


@router.post('/', status_code=HTTPStatus.CREATED, response_model=TrainerPublicSchema)
async def create_trainer(trainers: CreateTrainerSchema, session: Session):
    service = TrainerService(session)
    return await service.create(trainers)


@router.get(
    '/{trainer_id}/pokedex',
    response_model=LimitOffsetPage[PokedexPublicSchema] | list[PokedexPublicSchema],
)
async def get_trainer_pokedex(
    trainer_id: str,
    session: Session,
    current_trainer: CurrentTrainer,
    page_filter: Annotated[PokedexFilterPage, Depends()],
):
    service = TrainerService(session)
    return await service.list_pokedex(trainer_id, current_trainer, page_filter)


@router.get(
    '/{trainer_id}/pokemons',
    response_model=LimitOffsetPage[CapturedPokemonPublicSchema]
    | list[CapturedPokemonPublicSchema],
)
async def get_trainer_pokemons(
    trainer_id: str,
    session: Session,
    current_trainer: CurrentTrainer,
    page_filter: Annotated[CapturedPokemonFilterPage, Depends()],
):
    service = TrainerService(session)
    return await service.list_captured_pokemon(trainer_id, current_trainer, page_filter)


@router.post('/{trainer_id}/capture', response_model=CapturedPokemonPublicSchema)
async def trainer_capture_pokemons(
    trainer_id: str,
    session: Session,
    current_trainer: CurrentTrainer,
    capture_pokemon: CapturePokemonSchema,
):
    service = TrainerService(session)
    return await service.capture_pokemon(trainer_id, current_trainer, capture_pokemon)


@router.post('/{trainer_id}/battle')
async def trainer_battle(
    trainer_id: str,
    session: Session,
    current_trainer: CurrentTrainer,
    battle_pokemon: BattlePokemonSchema,
):
    service = TrainerService(session)
    return await service.battle(trainer_id, current_trainer, battle_pokemon)


@router.get('/{trainer_id}', status_code=HTTPStatus.OK, response_model=TrainerPublicSchema)
async def get_trainer(trainer_id: str, session: Session, current_trainer: CurrentTrainer):
    service = TrainerService(session)
    return await service.find_one(trainer_id, current_trainer)
