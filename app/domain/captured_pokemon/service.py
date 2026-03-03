"""Captured Pokemon Service - Manages trainer's caught pokemon collection."""

from datetime import datetime
from http import HTTPStatus
from typing import Annotated

from fastapi import Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.domain.captured_pokemon.model import CapturedPokemon
from app.domain.captured_pokemon.repository import CapturedPokemonRepository
from app.domain.captured_pokemon.schema import (
    CapturedPokemonFilterPage,
    CreateCapturedPokemonSchema,
    FindCapturePokemonSchema,
)
from app.domain.pokemon.business import PokemonBusiness
from app.domain.pokemon.model import Pokemon
from app.domain.trainer.model import Trainer

Session = Annotated[AsyncSession, Depends(get_session)]


class CapturedPokemonService:
    def __init__(self, session: Session):
        self.session = session
        self.business = PokemonBusiness()
        self.repository = CapturedPokemonRepository(session)

    async def create(
        self,
        pokemon: Pokemon,
        trainer: Trainer,
        nickname: str = None,
    ):
        stats = self.business.calculate_pokemon_stats(
            pokemon=pokemon,
        )

        create_captured_pokemon = CreateCapturedPokemonSchema(
            hp=stats['hp'],
            wins=stats['wins'],
            level=stats['level'],
            iv_hp=stats['iv_hp'],
            ev_hp=stats['ev_hp'],
            losses=stats['losses'],
            max_hp=stats['max_hp'],
            battles=stats['battles'],
            nickname=nickname if nickname else stats['nickname'],
            iv_speed=stats['iv_speed'],
            ev_speed=stats['ev_speed'],
            iv_attack=stats['iv_attack'],
            ev_attack=stats['ev_attack'],
            iv_defense=stats['iv_defense'],
            ev_defense=stats['ev_defense'],
            experience=stats['experience'],
            iv_special_attack=stats['iv_special_attack'],
            ev_special_attack=stats['ev_special_attack'],
            iv_special_defense=stats['iv_special_defense'],
            ev_special_defense=stats['ev_special_defense'],
            captured_at=datetime.now(),
            pokemon_id=pokemon.id,
            trainer_id=trainer.id,
        )
        return await self.repository.create(create_captured_pokemon)

    async def record_battle_win(
        self,
        captured_pokemon: CapturedPokemon,
        exp_gained: int = 0,
    ) -> CapturedPokemon:
        """
        Update captured pokemon after a battle win.

        Increments wins counter, adds experience points, and checks
        for level up based on growth rate formula.

        Args:
            captured_pokemon: The pokemon that won
            exp_gained: Experience points earned in battle

        Returns:
            Updated CapturedPokemon
        """
        captured_pokemon.wins += 1
        captured_pokemon.battles += 1
        captured_pokemon.experience += exp_gained

        # Check if pokemon should level up
        # Will need pokemon data to check growth rate formula
        # For now, just update the record

        await self.session.commit()
        await self.session.refresh(captured_pokemon)

        return captured_pokemon

    async def record_battle_loss(
        self,
        captured_pokemon: CapturedPokemon,
    ) -> CapturedPokemon:
        """
        Update captured pokemon after a battle loss.

        Increments losses counter and total battles count.

        Args:
            captured_pokemon: The pokemon that lost

        Returns:
            Updated CapturedPokemon
        """
        captured_pokemon.losses += 1
        captured_pokemon.battles += 1

        await self.session.commit()
        await self.session.refresh(captured_pokemon)

        return captured_pokemon

    async def add_effort_value(
        self,
        captured_pokemon: CapturedPokemon,
        ev_type: str,
        ev_amount: int = 1,
    ) -> CapturedPokemon:
        """
        Add effort value (EV) to a specific stat.

        Effort Values represent training in a specific stat.
        Used to recalculate stats for next level up.

        Args:
            captured_pokemon: The pokemon being trained
            ev_type: Type of stat (
            hp, attack, defense, special_attack, special_defense, speed
            )
            ev_amount: Amount of EV to add (default 1)

        Returns:
            Updated CapturedPokemon
        """
        ev_field = f'ev_{ev_type}'
        if hasattr(captured_pokemon, ev_field):
            current_ev = getattr(captured_pokemon, ev_field)
            # Cap EVs at 252 (max useful EVs per stat in Pokemon)
            setattr(captured_pokemon, ev_field, min(current_ev + ev_amount, 252))

        await self.session.commit()
        await self.session.refresh(captured_pokemon)

        return captured_pokemon

    async def recalculate_stats_for_level_up(
        self,
        captured_pokemon: CapturedPokemon,
        pokemon: Pokemon,
    ) -> CapturedPokemon:
        """
        Recalculate pokemon stats after level up.

        Uses current IVs and EVs to calculate new stats for current level.

        Args:
            captured_pokemon: The pokemon to recalculate
            pokemon: The pokemon species with base stats

        Returns:
            Updated CapturedPokemon with new stats
        """
        level = captured_pokemon.level

        # Recalculate with current IVs and EVs
        hp = max(
            1,
            (
                (2 * pokemon.hp + captured_pokemon.iv_hp + captured_pokemon.ev_hp // 4)
                * level
                // 100
            )
            + level
            + 5,
        )
        attack = max(
            1,
            (
                (
                    2 * pokemon.attack
                    + captured_pokemon.iv_attack
                    + captured_pokemon.ev_attack // 4
                )
                * level
                // 100
            )
            + 5,
        )
        defense = max(
            1,
            (
                (
                    2 * pokemon.defense
                    + captured_pokemon.iv_defense
                    + captured_pokemon.ev_defense // 4
                )
                * level
                // 100
            )
            + 5,
        )
        special_attack = max(
            1,
            (
                (
                    2 * pokemon.special_attack
                    + captured_pokemon.iv_special_attack
                    + captured_pokemon.ev_special_attack // 4
                )
                * level
                // 100
            )
            + 5,
        )
        special_defense = max(
            1,
            (
                (
                    2 * pokemon.special_defense
                    + captured_pokemon.iv_special_defense
                    + captured_pokemon.ev_special_defense // 4
                )
                * level
                // 100
            )
            + 5,
        )
        speed = max(
            1,
            (
                (
                    2 * pokemon.speed
                    + captured_pokemon.iv_speed
                    + captured_pokemon.ev_speed // 4
                )
                * level
                // 100
            )
            + 5,
        )

        # Update stats
        captured_pokemon.hp = hp
        captured_pokemon.max_hp = hp
        captured_pokemon.attack = attack
        captured_pokemon.defense = defense
        captured_pokemon.special_attack = special_attack
        captured_pokemon.special_defense = special_defense
        captured_pokemon.speed = speed

        await self.session.commit()
        await self.session.refresh(captured_pokemon)

        return captured_pokemon

    async def fetch_all(
        self,
        page_filter: Annotated[CapturedPokemonFilterPage, Query()],
    ):
        try:
            return await self.repository.list_all(page_filter=page_filter)
        except Exception as e:
            print(f'# => captured_pokemon => service => fetch_all => error => {e}')
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                detail='Error fetching captured_pokemons entries',
            )

    async def capture(self, trainer: Trainer, capture_pokemon: Pokemon, nickname: str = None):
        try:
            if trainer.pokeballs == 0:
                raise HTTPException(
                    status_code=HTTPStatus.FORBIDDEN, detail='Not enough pokeballs'
                )

            if trainer.capture_rate < capture_pokemon.capture_rate:
                raise HTTPException(
                    status_code=HTTPStatus.FORBIDDEN,
                    detail=(
                        f'You have {trainer.capture_rate} capture rate. '
                        f'To capture this Pokemon, you need '
                        f'{capture_pokemon.capture_rate}.'
                    ),
                )

            current_nickname = capture_pokemon.name

            exist_pokemon = await self.find_by_pokemon(
                find_capture_pokemon=FindCapturePokemonSchema(
                    trainer_id=trainer.id,
                    pokemon_id=capture_pokemon.id,
                )
            )

            if exist_pokemon and exist_pokemon.nickname == nickname:
                current_nickname = f'{capture_pokemon.name}_1'

            return await self.create(
                pokemon=capture_pokemon, trainer=trainer, nickname=current_nickname
            )
        except HTTPException:
            raise
        except Exception as e:
            print(f'# => captured_pokemon => service => capture => error => {e}')
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                detail='Error capture pokemons',
            )

    async def find_by_pokemon(self, find_capture_pokemon: FindCapturePokemonSchema):
        try:
            return await self.repository.find_by_pokemon(
                find_capture_pokemon=find_capture_pokemon
            )
        except Exception as e:
            print(f'# => captured_pokemon => service => find by pokemon => error => {e}')
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                detail='Error find by pokemon',
            )
