from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.domain.trainer.schema import (
    CreateTrainerSchema,
    InitializeTrainerSchema,
    TrainerPublicSchema,
)
from app.domain.trainer.service import TrainerService
from app.models.trainer import Trainer

router = APIRouter(prefix='/trainers', tags=['trainers'])
Service = Annotated[TrainerService, Depends()]
CurrentTrainer = Annotated[Trainer, Depends(get_current_user)]


@router.post('/', status_code=HTTPStatus.CREATED, response_model=TrainerPublicSchema)
async def create_trainer(trainers: CreateTrainerSchema, service: Service):
    return await service.create(trainers)


@router.post('/initialize', status_code=HTTPStatus.OK, response_model=TrainerPublicSchema)
async def initialize_trainer(
    current_trainer: CurrentTrainer, initialize: InitializeTrainerSchema, service: Service
):
    return await service.initialize(trainer=current_trainer, initialize_trainer=initialize)


@router.get('/{trainer_id}', status_code=HTTPStatus.OK, response_model=TrainerPublicSchema)
async def get_trainer(trainer_id: str, service: Service, current_trainer: CurrentTrainer):
    return await service.find_one(trainer_id, current_trainer)
