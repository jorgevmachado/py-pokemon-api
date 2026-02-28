from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_session
from app.domain.trainer.model import Trainer
from app.domain.trainer.schema import CreateTrainerSchema, FindOneUserSchemaParams
from app.shared.role_enum import RoleEnum
from app.shared.status_enum import StatusEnum

Session = Annotated[AsyncSession, Depends(get_session)]


class TrainerRepository:
    def __init__(self, session: Session):
        self.session = session

    async def create(self, create_trainer: CreateTrainerSchema) -> Trainer:
        trainer = Trainer(
            role=RoleEnum.USER,
            name=create_trainer.name,
            email=create_trainer.email,
            gender=create_trainer.gender,
            status=StatusEnum.ACTIVE,
            password=create_trainer.password,
            pokeballs=create_trainer.pokeballs,
            capture_rate=create_trainer.capture_rate,
            date_of_birth=create_trainer.date_of_birth,
            total_authentications=0,
            authentication_success=0,
            authentication_failures=0,
        )
        self.session.add(trainer)
        await self.session.commit()
        await self.session.refresh(trainer)
        return trainer

    async def update(self, trainer: Trainer) -> Trainer:
        await self.session.merge(trainer)
        await self.session.commit()
        await self.session.refresh(trainer)
        return trainer

    async def find_one(self, params: FindOneUserSchemaParams) -> Trainer | None:
        query = select(Trainer).options(
            selectinload(Trainer.pokedex), selectinload(Trainer.captured_pokemons)
        )

        if params.id:
            return await self.session.scalar(query.where(Trainer.id == params.id))
        if params.email:
            return await self.session.scalar(query.where(Trainer.email == params.email))
        return None
