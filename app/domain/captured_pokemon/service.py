"""Captured Pokemon Service - Manages user's caught pokemon collection."""

from datetime import datetime
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.domain.captured_pokemon.repository import CapturedPokemonRepository
from app.domain.captured_pokemon.schema import CreateCapturedPokemonSchema
from app.domain.pokemon.business import PokemonBusiness
from app.models import CapturedPokemon, Pokemon, User

Session = Annotated[AsyncSession, Depends(get_session)]


class CapturedPokemonService:
    def __init__(self, session: Session):
        self.session = session
        self.business = PokemonBusiness()
        self.repository = CapturedPokemonRepository(session)

    async def create(
        self,
        pokemon: Pokemon,
        user: User,
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
            nickname=stats['nickname'],
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
            trainer_id=user.id,
        )
        return await self.repository.create(create_captured_pokemon)

    async def create_captured_pokemon(
        self,
        pokemon: Pokemon,
        user: User,
        level: int = 1,
    ) -> CapturedPokemon:
        """
        Create a new captured pokemon entry for a user.

        Each captured pokemon instance is unique with randomly generated IVs
        (Individual Values) that determine its genetic potential across all stats.
        This ensures even two Pikachus will have different stat distributions.

        Formula used: Stat = ((2 * Base + IV + EV/4) * Level / 100) + 5

        Args:
            pokemon: The pokemon species being captured
            user: The user capturing the pokemon
            level: Starting level (default 1)

        Returns:
            CapturedPokemon instance with calculated stats
        """
        # Calculate unique stats for this pokemon instance
        stats = self.business.calculate_pokemon_stats(
            pokemon=pokemon,
            level=level,
        )

        captured_pokemon = CapturedPokemon(
            pokemon_id=pokemon.id,
            trainer_id=user.id,
            hp=stats['hp'],
            max_hp=stats['max_hp'],
            attack=stats['attack'],
            defense=stats['defense'],
            special_attack=stats['special_attack'],
            special_defense=stats['special_defense'],
            speed=stats['speed'],
            level=stats['level'],
            experience=stats['experience'],
            iv_hp=stats['iv_hp'],
            iv_attack=stats['iv_attack'],
            iv_defense=stats['iv_defense'],
            iv_special_attack=stats['iv_special_attack'],
            iv_special_defense=stats['iv_special_defense'],
            iv_speed=stats['iv_speed'],
            ev_hp=stats['ev_hp'],
            ev_attack=stats['ev_attack'],
            ev_defense=stats['ev_defense'],
            ev_special_attack=stats['ev_special_attack'],
            ev_special_defense=stats['ev_special_defense'],
            ev_speed=stats['ev_speed'],
            wins=stats['wins'],
            losses=stats['losses'],
            battles=stats['battles'],
            nickname=stats['nickname'],
            captured_at=datetime.utcnow(),
        )

        self.session.add(captured_pokemon)
        await self.session.commit()
        await self.session.refresh(captured_pokemon)

        return captured_pokemon

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
