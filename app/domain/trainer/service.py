from http import HTTPStatus
from typing import Annotated

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.security import get_password_hash
from app.domain.captured_pokemon.service import CapturedPokemonService
from app.domain.pokedex.service import PokedexService
from app.domain.pokemon.service import PokemonService
from app.domain.trainer.model import Trainer
from app.domain.trainer.repository import TrainerRepository
from app.domain.trainer.schema import (
    CreateTrainerSchema,
    FindOneUserSchemaParams,
)
from app.shared.status_enum import StatusEnum

Session = Annotated[AsyncSession, Depends(get_session)]


class TrainerService:
    def __init__(self, session: Session):
        self.repository = TrainerRepository(session)
        self.pokemon_service = PokemonService(session)
        self.pokedex_service = PokedexService(session)
        self.captured_pokemon_service = CapturedPokemonService(session)

    async def create(self, create_trainer: CreateTrainerSchema) -> Trainer:
        try:
            db_user = await self.repository.find_one(
                params=FindOneUserSchemaParams(email=create_trainer.email)
            )

            if db_user and db_user.email == create_trainer.email:
                raise HTTPException(
                    status_code=HTTPStatus.CONFLICT,
                    detail='Email already exists',
                )
            create_trainer.password = get_password_hash(create_trainer.password)
            trainer = await self.repository.create(create_trainer)

            first_pokemon = await self.pokemon_service.first_pokemon(
                create_trainer.pokemon_name
            )

            await self.pokedex_service.initialize(
                trainer=trainer,
                pokemon=first_pokemon.pokemon,
                pokemons=first_pokemon.pokemons,
            )

            await self.captured_pokemon_service.create(
                trainer=trainer,
                pokemon=first_pokemon.pokemon,
            )
            trainer.status = StatusEnum.ACTIVE
            return await self.repository.update(trainer=trainer)
        except HTTPException:
            raise
        except Exception as e:
            print(f'# => TrainerService => create => error => {e}')
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                detail='Error creating trainer',
            )

    async def find_one(self, Trainer_id: str, trainer: Trainer) -> Trainer:
        db_user = await self.repository.find_one(params=FindOneUserSchemaParams(id=Trainer_id))

        if not db_user:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Trainer not found')

        if trainer.id != Trainer_id:
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions'
            )

        return db_user

    async def find_one_by_email(self, email: str) -> Trainer:
        return await self.repository.find_one(params=FindOneUserSchemaParams(email=email))

    async def update(self, trainer: Trainer):
        return await self.repository.update(trainer=trainer)
