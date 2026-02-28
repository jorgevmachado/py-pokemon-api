from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.security import get_current_user
from app.domain.trainer.model import Trainer
from app.domain.trainer.schema import (
    CreateTrainerSchema,
    TrainerInitializeTrainerSchema,
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


@router.post('/initialize', response_model=TrainerPublicSchema)
async def initialize(
    session: Session, params: TrainerInitializeTrainerSchema, current_trainer: CurrentTrainer
):
    service = TrainerService(session)
    return await service.initialize(params, current_trainer)


@router.get('/{trainer_id}', status_code=HTTPStatus.OK, response_model=TrainerPublicSchema)
async def get_trainer(trainer_id: str, session: Session, current_trainer: CurrentTrainer):
    service = TrainerService(session)
    return await service.find_one(trainer_id, current_trainer)
