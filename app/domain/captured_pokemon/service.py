"""Captured Pokemon Service - Manages trainer's caught pokemon collection."""

import logging
from datetime import datetime
from http import HTTPStatus
from typing import Annotated, Optional

from fastapi import Depends, HTTPException

from app.core.exceptions.exceptions import handle_service_exception
from app.core.logging import LoggingParams, log_service_success
from app.domain.captured_pokemon.repository import CapturedPokemonRepository
from app.domain.captured_pokemon.schema import (
    CapturePokemonHealSchema,
    CapturePokemonSchema,
    PartialCapturedPokemonSchema,
)
from app.domain.move.business import PokemonMoveBusiness
from app.domain.pokedex.service import PokemonService
from app.domain.progression.business import PokemonProgressionBusiness
from app.models.captured_pokemon import CapturedPokemon
from app.models.pokemon import Pokemon
from app.models.trainer import Trainer
from app.shared.schemas import FilterPage

Repository = Annotated[CapturedPokemonRepository, Depends()]
PokemonService = Annotated[PokemonService, Depends()]
logger = logging.getLogger(__name__)


class CapturedPokemonService:
    def __init__(self, repository: Repository, pokemon_service: PokemonService):
        self.business = PokemonProgressionBusiness()
        self.pokemon_service = pokemon_service
        self.repository = repository
        self.logger_params = LoggingParams(
            logger=logger, service='captured_pokemon', operation=''
        )

    async def create(
        self,
        pokemon: Pokemon,
        trainer: Trainer,
        nickname: str = None,
    ):
        exist_captured_pokemon = await self.repository.find_by(
            trainer_id=trainer.id,
            pokemon_id=pokemon.id,
        )
        if not exist_captured_pokemon:
            stats = self.business.initialize_stats(
                pokemon=pokemon,
            )

            captured_pokemon = await self.repository.save(
                entity=CapturedPokemon(
                    hp=stats.hp,
                    wins=stats.wins,
                    level=stats.level,
                    iv_hp=stats.iv_hp,
                    ev_hp=stats.ev_hp,
                    losses=stats.losses,
                    max_hp=stats.max_hp,
                    battles=stats.battles,
                    nickname=nickname if nickname else pokemon.name,
                    speed=stats.speed,
                    iv_speed=stats.iv_speed,
                    ev_speed=stats.ev_speed,
                    attack=stats.attack,
                    iv_attack=stats.iv_attack,
                    ev_attack=stats.ev_attack,
                    defense=stats.defense,
                    iv_defense=stats.iv_defense,
                    ev_defense=stats.ev_defense,
                    experience=stats.experience,
                    special_attack=stats.special_attack,
                    iv_special_attack=stats.iv_special_attack,
                    ev_special_attack=stats.ev_special_attack,
                    special_defense=stats.special_defense,
                    iv_special_defense=stats.iv_special_defense,
                    ev_special_defense=stats.ev_special_defense,
                    captured_at=datetime.now(),
                    pokemon_id=pokemon.id,
                    trainer_id=trainer.id,
                    formula=stats.formula,
                )
            )

            pokemon_move_business = PokemonMoveBusiness()
            selected_moves = pokemon_move_business.select_random_moves(pokemon.moves)
            captured_pokemon.moves = selected_moves
            log_service_success(
                self.logger_params,
                operation='create',
                message='Create Captured Pokemon not exists successfully',
            )
            return await self.repository.update(captured_pokemon)
        log_service_success(
            self.logger_params,
            operation='create',
            message='Create Captured Pokemon exists successfully',
        )
        return exist_captured_pokemon

    async def fetch_all(
        self,
        trainer_id: str,
        page_filter: Optional[FilterPage] = None,
    ):
        try:
            log_service_success(
                self.logger_params,
                operation='fetch_all',
                message='Fetch All Captured Pokemon successfully',
            )

            return await self.repository.list_all(
                page_filter=FilterPage.build(page_filter, trainer_id=trainer_id)
            )
        except Exception as exception:
            handle_service_exception(
                exception,
                logger=self.logger_params.logger,
                service=self.logger_params.service,
                operation='create',
            )

    async def capture(self, trainer: Trainer, capture_pokemon: CapturePokemonSchema):
        try:
            pokemon = await self.pokemon_service.fetch_one(name=capture_pokemon.pokemon_name)

            if trainer.pokeballs == 0:
                raise HTTPException(
                    status_code=HTTPStatus.FORBIDDEN, detail='Not enough pokeballs'
                )

            if trainer.capture_rate < pokemon.capture_rate:
                raise HTTPException(
                    status_code=HTTPStatus.FORBIDDEN,
                    detail=(
                        f'You have {trainer.capture_rate} capture rate. '
                        f'To capture this Pokemon, you need '
                        f'{pokemon.capture_rate}.'
                    ),
                )

            current_nickname = pokemon.name

            if capture_pokemon.nickname:
                current_nickname = capture_pokemon.nickname

            exist_pokemon = await self.repository.find_by(
                trainer_id=trainer.id,
                pokemon_id=pokemon.id,
            )

            if exist_pokemon and exist_pokemon.nickname == current_nickname:
                current_nickname = f'{pokemon.name}_1'

            log_service_success(
                self.logger_params, operation='capture', message='Capture Pokemon successfully'
            )

            return await self.create(
                pokemon=pokemon, trainer=trainer, nickname=current_nickname
            )
        except Exception as exception:
            handle_service_exception(
                exception,
                logger=self.logger_params.logger,
                service=self.logger_params.service,
                operation='capture',
            )

    async def update(
        self, captured_pokemon_id: str, captured_pokemon_update: PartialCapturedPokemonSchema
    ):
        captured_pokemon = await self.repository.find_by(id=captured_pokemon_id)
        if not captured_pokemon:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, detail='Captured Pokemon not found'
            )

        log_service_success(
            self.logger_params,
            operation='update',
            message='Update Captured Pokemon successfully',
        )

        if captured_pokemon_update.level is not None:
            captured_pokemon.level = captured_pokemon_update.level

        if captured_pokemon_update.wins is not None:
            captured_pokemon.wins = captured_pokemon_update.wins

        if captured_pokemon_update.losses is not None:
            captured_pokemon.losses = captured_pokemon_update.losses

        if captured_pokemon_update.hp is not None:
            captured_pokemon.hp = captured_pokemon_update.hp

        if captured_pokemon_update.speed is not None:
            captured_pokemon.speed = captured_pokemon_update.speed

        if captured_pokemon_update.attack is not None:
            captured_pokemon.attack = captured_pokemon_update.attack

        if captured_pokemon_update.defense is not None:
            captured_pokemon.defense = captured_pokemon_update.defense

        if captured_pokemon_update.attack is not None:
            captured_pokemon.attack = captured_pokemon_update.attack

        if captured_pokemon_update.special_attack is not None:
            captured_pokemon.special_attack = captured_pokemon_update.special_attack

        if captured_pokemon_update.special_defense is not None:
            captured_pokemon.special_defense = captured_pokemon_update.special_defense

        if captured_pokemon_update.experience is not None:
            captured_pokemon.experience = captured_pokemon_update.experience

        return await self.repository.update(captured_pokemon)

    async def heal(self, trainer_id: str, heal_pokemons: CapturePokemonHealSchema):
        if heal_pokemons.all:
            pokemons_to_heal = await self.repository.list_all(trainer_id=trainer_id)
        else:
            pokemons_to_heal = []
            for pokemon_id in heal_pokemons.pokemons:
                pokemon = await self.repository.find_by(id=pokemon_id)
                if pokemon and pokemon.trainer_id == trainer_id:
                    pokemons_to_heal.append(pokemon)

        for pokemon in pokemons_to_heal:
            pokemon.hp = pokemon.max_hp
            await self.repository.update(pokemon)

        log_service_success(
            self.logger_params, operation='heal', message='Heal Captured Pokemon successfully'
        )
        return pokemons_to_heal
