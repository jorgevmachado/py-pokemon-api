import logging
from datetime import datetime
from http import HTTPStatus
from typing import Annotated, Optional

from fastapi import Depends, HTTPException, Query

from app.domain.pokedex.model import Pokedex
from app.domain.pokedex.repository import PokedexRepository
from app.domain.pokedex.schema import (
    CreatePokedexSchema,
    FindPokedexSchema,
    PartialPokedexSchema,
    PokedexFilterPage,
)
from app.domain.pokemon.model import Pokemon
from app.domain.pokemon.service import PokemonService
from app.domain.progression.business import PokemonProgressionBusiness
from app.domain.trainer.model import Trainer
from app.shared.exceptions import handle_service_exception, log_service_exception

Repository = Annotated[PokedexRepository, Depends()]
PokemonService = Annotated[PokemonService, Depends()]
logger = logging.getLogger(__name__)


class PokedexService:
    def __init__(self, repository: Repository, pokemon_service: PokemonService):
        self.repository = repository
        self.pokemon_service = pokemon_service
        self.business = PokemonProgressionBusiness()

    async def initialize_pokemon(
        self, pokemon: Pokemon, trainer_id: str, discovered: bool = False
    ) -> Pokedex | None:
        try:
            stats = self.business.initialize_stats(pokemon=pokemon)

            create_pokedex = CreatePokedexSchema(
                hp=stats.hp,
                wins=stats.wins,
                level=stats.level,
                iv_hp=stats.iv_hp,
                ev_hp=stats.ev_hp,
                losses=stats.losses,
                max_hp=stats.max_hp,
                battles=stats.battles,
                nickname=pokemon.name,
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
                discovered=discovered,
                discovered_at=None,
                pokemon_id=pokemon.id,
                trainer_id=trainer_id,
                formula=stats.formula,
            )
            return await self.repository.create(create_pokedex)
        except Exception as exception:
            log_service_exception(
                exception,
                logger=logger,
                service='pokedex',
                operation='initialize_pokemon',
            )
        return None

    async def initialize(
        self,
        trainer: Trainer,
        pokemon: Optional[Pokemon],
        pokemons: list[Pokemon],
    ) -> list[Pokedex]:
        try:
            new_entries: list[Pokedex] = []
            pokemon_name = pokemon.name if pokemon else None

            existing_pokemon_ids = await self.repository.find_by_trainer(trainer.id)

            for item in pokemons:
                if item.id in existing_pokemon_ids:
                    continue

                create_pokedex = await self.initialize_pokemon(
                    pokemon=item, trainer_id=trainer.id, discovered=item.name == pokemon_name
                )

                new_entries.append(create_pokedex)

            return new_entries
        except Exception as exception:
            log_service_exception(
                exception,
                logger=logger,
                service='pokedex',
                operation='initialize',
            )
        return []

    async def fetch_all(
        self,
        trainer_id: str,
        page_filter: Annotated[PokedexFilterPage, Query()] = None,
    ):
        try:
            return await self.repository.list_all(
                trainer_id=trainer_id, page_filter=page_filter
            )
        except Exception as exception:
            handle_service_exception(
                exception,
                logger=logger,
                service='pokedex',
                operation='fetch_all',
            )

    async def refresh(self, trainer_id: str, pokemons: list[Pokemon]):
        total_not_exist = 0
        new_entries: list[Pokedex] = []
        for pokemon in pokemons:
            exist_pokedex = await self.repository.find_by_pokemon(
                FindPokedexSchema(trainer_id=trainer_id, pokemon_id=pokemon.id)
            )
            if not exist_pokedex:
                total_not_exist += 1

                create_pokedex = await self.initialize_pokemon(
                    pokemon=pokemon, trainer_id=trainer_id, discovered=False
                )

                new_entries.append(create_pokedex)
        print(
            f'# LOG => pokedex => service => refresh => total_not_exist => {total_not_exist}'
        )
        return new_entries

    async def find_by_pokemon(self, find_pokedex: FindPokedexSchema):
        try:
            return await self.repository.find_by_pokemon(find_pokedex=find_pokedex)
        except Exception as exception:
            handle_service_exception(
                exception,
                logger=logger,
                service='pokedex',
                operation='find_by_pokemon',
            )

    async def discovered(self, trainer_id: str, pokemon: Pokemon, discovered: bool):
        pokedex = await self.find_by_pokemon(
            find_pokedex=FindPokedexSchema(trainer_id=trainer_id, pokemon_id=pokemon.id)
        )

        if not pokedex.discovered:
            pokedex.discovered = discovered
            stats = self.business.initialize_stats(pokemon=pokemon)
            pokedex.hp = stats.hp
            pokedex.wins = stats.wins
            pokedex.level = stats.level
            pokedex.iv_hp = stats.iv_hp
            pokedex.ev_hp = stats.ev_hp
            pokedex.losses = stats.losses
            pokedex.max_hp = stats.max_hp
            pokedex.battles = stats.battles
            pokedex.nickname = pokemon.name
            pokedex.speed = stats.speed
            pokedex.iv_speed = stats.iv_speed
            pokedex.ev_speed = stats.ev_speed
            pokedex.attack = stats.attack
            pokedex.iv_attack = stats.iv_attack
            pokedex.ev_attack = stats.ev_attack
            pokedex.defense = stats.defense
            pokedex.iv_defense = stats.iv_defense
            pokedex.ev_defense = stats.ev_defense
            pokedex.experience = stats.experience
            pokedex.special_attack = stats.special_attack
            pokedex.iv_special_attack = stats.iv_special_attack
            pokedex.ev_special_attack = stats.ev_special_attack
            pokedex.special_defense = stats.special_defense
            pokedex.iv_special_defense = stats.iv_special_defense
            pokedex.ev_special_defense = stats.ev_special_defense
            if discovered:
                pokedex.discovered_at = datetime.now()
            pokedex.formula = stats.formula
            await self.repository.update(pokedex)
            return pokedex

        return pokedex

    async def discover(self, trainer_id: str, pokemon_name: str):
        pokemon = await self.pokemon_service.fetch_one(name=pokemon_name)

        pokedex = await self.find_by_pokemon(
            find_pokedex=FindPokedexSchema(trainer_id=trainer_id, pokemon_id=pokemon.id)
        )

        if not pokedex.discovered:
            pokedex.discovered = True
            stats = self.business.initialize_stats(pokemon=pokemon)
            pokedex.hp = stats.hp
            pokedex.wins = stats.wins
            pokedex.level = stats.level
            pokedex.iv_hp = stats.iv_hp
            pokedex.ev_hp = stats.ev_hp
            pokedex.losses = stats.losses
            pokedex.max_hp = stats.max_hp
            pokedex.battles = stats.battles
            pokedex.nickname = pokemon.name
            pokedex.speed = stats.speed
            pokedex.iv_speed = stats.iv_speed
            pokedex.ev_speed = stats.ev_speed
            pokedex.attack = stats.attack
            pokedex.iv_attack = stats.iv_attack
            pokedex.ev_attack = stats.ev_attack
            pokedex.defense = stats.defense
            pokedex.iv_defense = stats.iv_defense
            pokedex.ev_defense = stats.ev_defense
            pokedex.experience = stats.experience
            pokedex.special_attack = stats.special_attack
            pokedex.iv_special_attack = stats.iv_special_attack
            pokedex.ev_special_attack = stats.ev_special_attack
            pokedex.special_defense = stats.special_defense
            pokedex.iv_special_defense = stats.iv_special_defense
            pokedex.ev_special_defense = stats.ev_special_defense
            pokedex.discovered_at = datetime.now()
            pokedex.formula = stats.formula
            await self.repository.update(pokedex)
            return pokedex

        return pokedex

    async def update(self, pokedex_id: str, pokedex_update: PartialPokedexSchema):
        pokedex = await self.repository.find_by_id(pokedex_id)
        if not pokedex:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Pokedex not found')

        for key, value in pokedex_update.model_dump().items():
            setattr(pokedex, key, value)

        return await self.repository.update(pokedex)
