from http import HTTPStatus
from typing import Annotated

from fastapi import Depends, HTTPException, Query

from app.core.security import get_password_hash
from app.domain.captured_pokemon.schema import (
    CapturedPokemonFilterPage,
    CapturePokemonSchema,
    FindCapturePokemonSchema,
)
from app.domain.captured_pokemon.service import CapturedPokemonService
from app.domain.pokedex.schema import FindPokedexSchema, PokedexFilterPage
from app.domain.pokedex.service import PokedexService
from app.domain.pokemon.service import PokemonService
from app.domain.trainer.model import Trainer
from app.domain.trainer.repository import TrainerRepository
from app.domain.trainer.schema import (
    BattlePokemonSchema,
    CreateTrainerSchema,
    FindOneUserSchemaParams,
)
from app.shared.status_enum import StatusEnum

Repository = Annotated[TrainerRepository, Depends()]
PokemonService = Annotated[PokemonService, Depends()]
PokedexService = Annotated[PokedexService, Depends()]
CapturedPokemonService = Annotated[CapturedPokemonService, Depends()]


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

    async def find_one(self, trainer_id: str, trainer: Trainer) -> Trainer:
        db_user = await self.repository.find_one(params=FindOneUserSchemaParams(id=trainer_id))

        if not db_user:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Trainer not found')

        if trainer.id != trainer_id:
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions'
            )

        pokemon_total = await self.pokemon_service.total()
        total_pokedex = len(db_user.pokedex)
        pokemons = await self.pokemon_service.fetch_all()
        if total_pokedex < pokemon_total:
            await self.pokedex_service.refresh(trainer_id=db_user.id, pokemons=pokemons)
        return db_user

    async def find_one_by_email(self, email: str) -> Trainer:
        return await self.repository.find_one(params=FindOneUserSchemaParams(email=email))

    async def update(self, trainer: Trainer):
        return await self.repository.update(trainer=trainer)

    async def list_pokedex(
        self,
        trainer_id: str,
        current_trainer: Trainer,
        page_filter: Annotated[PokedexFilterPage, Query()],
    ):
        try:
            db_trainer = await self.find_one(trainer_id, current_trainer)

            page_filter.trainer_id = db_trainer.id
            return await self.pokedex_service.fetch_all(
                page_filter=page_filter,
            )
        except HTTPException:
            raise
        except Exception as e:
            print(f'# => TrainerService => list_pokedex => error => {e}')
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                detail='Error getting trainer pokedex',
            )

    async def list_captured_pokemon(
        self,
        trainer_id: str,
        current_trainer: Trainer,
        page_filter: Annotated[CapturedPokemonFilterPage, Query()],
    ):
        try:
            db_trainer = await self.find_one(trainer_id, current_trainer)

            page_filter.trainer_id = db_trainer.id
            return await self.captured_pokemon_service.fetch_all(
                page_filter=page_filter,
            )
        except HTTPException:
            raise
        except Exception as e:
            print(f'# => TrainerService => list_captured_pokemon => error => {e}')
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                detail='Error getting trainer pokemons',
            )

    async def capture_pokemon(
        self, trainer_id: str, current_trainer: Trainer, capture_pokemon: CapturePokemonSchema
    ):
        try:
            db_trainer = await self.find_one(trainer_id, current_trainer)

            pokemon = await self.pokemon_service.fetch_one(name=capture_pokemon.pokemon_name)

            return await self.captured_pokemon_service.capture(
                trainer=db_trainer,
                capture_pokemon=pokemon,
            )
        except HTTPException:
            raise
        except Exception as e:
            print(f'# => TrainerService => capture_pokemon => error => {e}')
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                detail='Error trainer capture pokemon',
            )

    async def battle(
        self, trainer_id: str, current_trainer: Trainer, battle_pokemon: BattlePokemonSchema
    ):

        try:
            db_trainer = await self.find_one(trainer_id, current_trainer)

            trainer_pokemon = await self.captured_pokemon_service.find_by_pokemon(
                FindCapturePokemonSchema(
                    trainer_id=db_trainer.id, name=battle_pokemon.trainer_pokemon
                )
            )
            if not trainer_pokemon:
                raise HTTPException(
                    status_code=HTTPStatus.NOT_FOUND, detail='Trainer Pokemon not found'
                )

            if trainer_pokemon.hp <= 0:
                raise HTTPException(
                    status_code=HTTPStatus.BAD_REQUEST, detail='Trainer Pokemon is fainted'
                )

            opponent_pokemon = await self.pokedex_service.find_by_pokemon(
                FindPokedexSchema(
                    trainer_id=db_trainer.id, name=battle_pokemon.opponent_pokemon
                )
            )

            if not opponent_pokemon:
                raise HTTPException(
                    status_code=HTTPStatus.NOT_FOUND,
                    detail='Opponent Pokedex Pokemon not found',
                )

            if opponent_pokemon.hp <= 0:
                raise HTTPException(
                    status_code=HTTPStatus.BAD_REQUEST, detail='Opponent Pokemon is fainted'
                )

            return None
        except HTTPException:
            raise
        except Exception as e:
            print(f'# => TrainerService => battle => error => {e}')
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                detail='Error battle pokemon',
            )
