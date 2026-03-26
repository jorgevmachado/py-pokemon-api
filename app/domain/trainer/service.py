import logging
from http import HTTPStatus
from typing import Annotated

from fastapi import Depends, HTTPException

from app.core.exceptions.exceptions import handle_service_exception
from app.core.logging import LoggingParams, log_service_success
from app.core.security import get_password_hash
from app.core.service import BaseService
from app.domain.battle.business import PokemonBattleBusiness
from app.domain.captured_pokemon.service import CapturedPokemonService
from app.domain.pokedex.service import PokedexService
from app.domain.pokemon.service import PokemonService
from app.domain.trainer.repository import TrainerRepository
from app.domain.trainer.schema import (
    CreateTrainerSchema,
    InitializeTrainerSchema,
)
from app.models.trainer import Trainer
from app.shared.enums.role_enum import RoleEnum
from app.shared.enums.status_enum import StatusEnum

Repository = Annotated[TrainerRepository, Depends()]
PokemonService = Annotated[PokemonService, Depends()]
PokedexService = Annotated[PokedexService, Depends()]
CapturedPokemonService = Annotated[CapturedPokemonService, Depends()]
logger = logging.getLogger(__name__)


class TrainerService(BaseService[Repository, Trainer]):
    def __init__(
        self,
        repository: Repository,
        pokemon_service: PokemonService,
        pokedex_service: PokedexService,
        captured_pokemon_service: CapturedPokemonService,
    ):
        self.pokemon_service = pokemon_service
        self.pokedex_service = pokedex_service
        self.captured_pokemon_service = captured_pokemon_service
        self.battle_business = PokemonBattleBusiness()
        logger_params = LoggingParams(logger=logger, service='trainer', operation='')
        super().__init__(repository, logger_params)

    async def create(self, create_trainer: CreateTrainerSchema) -> Trainer:
        try:
            db_user = await self.find_one_by_email(email=create_trainer.email)

            if db_user and db_user.email == create_trainer.email:
                raise HTTPException(
                    status_code=HTTPStatus.CONFLICT,
                    detail='Email already exists',
                )

            trainer = await self.repository.save(
                Trainer(
                    role=RoleEnum.USER,
                    name=create_trainer.name,
                    email=create_trainer.email,
                    gender=create_trainer.gender,
                    status=StatusEnum.INCOMPLETE,
                    password=get_password_hash(create_trainer.password),
                    pokeballs=create_trainer.pokeballs,
                    capture_rate=create_trainer.capture_rate,
                    date_of_birth=create_trainer.date_of_birth,
                    total_authentications=0,
                    authentication_success=0,
                    authentication_failures=0,
                )
            )

            await self.pokemon_service.list_all()
            log_service_success(
                self.logger_params, operation='create', message='Trainer created successfully'
            )
            return trainer
        except HTTPException:
            raise
        except Exception as exception:
            handle_service_exception(
                exception,
                logger=self.logger_params.logger,
                service=self.logger_params.service,
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

            log_service_success(
                self.logger_params,
                operation='initialize',
                message='Trainer initialize successfully',
            )
            return await self.repository.update(db_user)
        log_service_success(
            self.logger_params, operation='initialize', message='Trainer already initialized'
        )
        return trainer

    async def find_one(self, trainer_id: str, trainer: Trainer) -> Trainer:
        db_user = await self.repository.find_by(id=trainer_id)

        if not db_user:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Trainer not found')

        if trainer.id != trainer_id:
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions'
            )
        log_service_success(
            self.logger_params, operation='find_one', message='Find One Trainer successfully'
        )
        return db_user

    async def find_one_by_email(self, email: str) -> Trainer:
        log_service_success(
            self.logger_params,
            operation='find_one_by_email',
            message='Find One Trainer by email successfully',
        )
        return await self.repository.find_by(email=email)

    async def update(self, trainer: Trainer):
        log_service_success(
            self.logger_params, operation='update', message='Update Trainer successfully'
        )
        return await self.repository.update(entity=trainer)
