import logging
from http import HTTPStatus
from typing import Annotated

from fastapi import Depends, HTTPException

from app.core.security import get_password_hash
from app.domain.battle.business import PokemonBattleBusiness
from app.domain.captured_pokemon.service import CapturedPokemonService
from app.domain.pokedex.service import PokedexService
from app.domain.pokemon.service import PokemonService
from app.domain.trainer.model import Trainer
from app.domain.trainer.repository import TrainerRepository
from app.domain.trainer.schema import (
    CreateTrainerSchema,
    FindOneUserSchemaParams,
    InitializeTrainerSchema,
)
from app.shared.exceptions import handle_service_exception
from app.shared.status_enum import StatusEnum

Repository = Annotated[TrainerRepository, Depends()]
PokemonService = Annotated[PokemonService, Depends()]
PokedexService = Annotated[PokedexService, Depends()]
CapturedPokemonService = Annotated[CapturedPokemonService, Depends()]
logger = logging.getLogger(__name__)


class TrainerService:
    def __init__(
        self,
        repository: Repository,
        pokemon_service: PokemonService,
        pokedex_service: PokedexService,
        captured_pokemon_service: CapturedPokemonService,
    ):
        self.repository = repository
        self.pokemon_service = pokemon_service
        self.pokedex_service = pokedex_service
        self.captured_pokemon_service = captured_pokemon_service
        self.battle_business = PokemonBattleBusiness()

    async def create(self, create_trainer: CreateTrainerSchema) -> Trainer:
        try:
            db_user = await self.find_one_by_email(email=create_trainer.email)

            if db_user and db_user.email == create_trainer.email:
                raise HTTPException(
                    status_code=HTTPStatus.CONFLICT,
                    detail='Email already exists',
                )
            create_trainer.password = get_password_hash(create_trainer.password)
            create_trainer.status = StatusEnum.INCOMPLETE
            trainer = await self.repository.create(create_trainer)

            await self.pokemon_service.initialize()
            return trainer
        except HTTPException:
            raise
        except Exception as exception:
            handle_service_exception(
                exception,
                logger=logger,
                service='trainer',
                operation='create',
            )

    async def initialize(
        self, trainer: Trainer, initialize_trainer: InitializeTrainerSchema
    ) -> Trainer:
        db_user = await self.find_one(trainer_id=trainer.id, trainer=trainer)

        if db_user.status == StatusEnum.INCOMPLETE:
            first_pokemon = await self.pokemon_service.first_pokemon(
                initialize_trainer.pokemon_name
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
            db_user.status = StatusEnum.ACTIVE
            pokemon_capture_rate = first_pokemon.pokemon.capture_rate

            if initialize_trainer.capture_rate < pokemon_capture_rate:
                db_user.capture_rate = pokemon_capture_rate

            return await self.repository.update(db_user)

        return trainer

    async def find_one(self, trainer_id: str, trainer: Trainer) -> Trainer:
        db_user = await self.repository.find_one(params=FindOneUserSchemaParams(id=trainer_id))

        if not db_user:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Trainer not found')

        if trainer.id != trainer_id:
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions'
            )

        return db_user

    async def find_one_by_email(self, email: str) -> Trainer:
        return await self.repository.find_one(params=FindOneUserSchemaParams(email=email))

    async def update(self, trainer: Trainer):
        return await self.repository.update(trainer=trainer)
