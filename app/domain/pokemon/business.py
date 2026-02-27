import random
from typing import Optional

from sqlalchemy import inspect

from app.domain.pokemon.external.schemas.evolution import (
    PokemonExternalEvolutionChainEvolvesToSchemaResponse,
    PokemonExternalEvolutionChainSchemaResponse,
)
from app.domain.pokemon.schema import PokemonSchema
from app.models import Pokemon
from app.models.growth_rate import PokemonGrowthRate
from app.shared.status_enum import StatusEnum


class PokemonBusiness:
    def ensure_evolution(
        self,
        params: Optional[PokemonExternalEvolutionChainSchemaResponse] = None,
    ) -> list[str]:
        if not params:
            return []

        return [
            params.species.name,
            *self.ensure_next_evolution(params.evolves_to),
        ]

    def ensure_next_evolution(
        self,
        params: Optional[list[PokemonExternalEvolutionChainEvolvesToSchemaResponse]] = None,
    ) -> list[str]:
        if not params:
            return []

        return [
            name
            for item in params
            for name in [
                item.species.name,
                *self.ensure_next_evolution(item.evolves_to),
            ]
        ]

    @staticmethod
    def merge_if_changed(
        pokemon_target: Pokemon,
        pokemon_source: PokemonSchema,
    ) -> Pokemon:
        mapper = inspect(Pokemon)

        for column in mapper.columns:
            key = column.key
            source_value = getattr(pokemon_source, key, None)

            if source_value is not None:
                current_value = getattr(pokemon_target, key)
                if current_value != source_value:
                    setattr(pokemon_target, key, source_value)
        return pokemon_target

    @staticmethod
    def find_first_pokemon(
        pokemons: list[Pokemon],
        pokemon_name: str | None = None,
    ) -> Optional[Pokemon]:
        if not pokemons:
            return None

        if not pokemon_name:
            return PokemonBusiness.get_random_pokemon(pokemons=pokemons)

        return next(
            (p for p in pokemons if p.name == pokemon_name),
            None,
        )

    @staticmethod
    def get_random_pokemon(pokemons: list[Pokemon]) -> Optional[Pokemon]:
        if not pokemons:
            return None

        pokemon_complete = next(
            (p for p in pokemons if p.status == StatusEnum.COMPLETE),
            None,
        )
        if pokemon_complete:
            return pokemon_complete

        orders = [p.order for p in pokemons]
        random_order = orders[int(__import__('random').random() * len(orders))]
        return next(
            (p for p in pokemons if p.order == random_order),
            None,
        )

    @staticmethod
    def calculate_pokemon_stats(
        pokemon: Pokemon,
        level: int = 1,
    ) -> dict:
        """
        Calculate initial pokemon stats based on base stats and growth rate formula.

        Args:
            pokemon: Pokemon model with base stats
            level: Starting level (default 1)

        Returns:
            Dictionary with calculated stats for pokedex and captured_pokemon
        """
        if not pokemon:
            return {}

        base_stats = PokemonBusiness._build_base_stats(pokemon)
        experience = PokemonBusiness._calculate_experience(
            pokemon.growth_rate,
            level,
        )
        ivs = PokemonBusiness._build_ivs(base_stats)
        evs = PokemonBusiness._build_evs(base_stats)
        stats = PokemonBusiness._build_stats(base_stats, ivs, evs, level)

        return {
            'hp': stats['hp'],
            'max_hp': stats['hp'],
            'attack': stats['attack'],
            'defense': stats['defense'],
            'special_attack': stats['special_attack'],
            'special_defense': stats['special_defense'],
            'speed': stats['speed'],
            'level': level,
            'experience': experience,
            'iv_hp': ivs['hp'],
            'iv_attack': ivs['attack'],
            'iv_defense': ivs['defense'],
            'iv_special_attack': ivs['special_attack'],
            'iv_special_defense': ivs['special_defense'],
            'iv_speed': ivs['speed'],
            'ev_hp': evs['hp'],
            'ev_attack': evs['attack'],
            'ev_defense': evs['defense'],
            'ev_special_attack': evs['special_attack'],
            'ev_special_defense': evs['special_defense'],
            'ev_speed': evs['speed'],
            'wins': 0,
            'losses': 0,
            'battles': 0,
            'nickname': pokemon.name,
        }

    @staticmethod
    def _build_base_stats(pokemon: Pokemon) -> dict[str, int]:
        return {
            'hp': pokemon.hp or 0,
            'attack': pokemon.attack or 0,
            'defense': pokemon.defense or 0,
            'special_attack': pokemon.special_attack or 0,
            'special_defense': pokemon.special_defense or 0,
            'speed': pokemon.speed or 0,
        }

    @staticmethod
    def _build_ivs(base_stats: dict[str, int]) -> dict[str, int]:
        return {name: random.randint(0, 31) for name in base_stats}

    @staticmethod
    def _build_evs(base_stats: dict[str, int]) -> dict[str, int]:
        return {name: 0 for name in base_stats}

    @staticmethod
    def _build_stats(
        base_stats: dict[str, int],
        ivs: dict[str, int],
        evs: dict[str, int],
        level: int,
    ) -> dict[str, int]:
        return {
            name: PokemonBusiness._calculate_stat_value(
                base_stats[name],
                ivs[name],
                evs[name],
                level,
                name == 'hp',
            )
            for name in base_stats
        }

    @staticmethod
    def _calculate_stat_value(
        base: int,
        iv: int,
        ev: int,
        level: int,
        is_hp: bool,
    ) -> int:
        value = ((2 * base + iv + ev // 4) * level // 100) + 5
        if is_hp:
            value += level
        return max(1, value)

    @staticmethod
    def _calculate_experience(
        growth_rate: PokemonGrowthRate | None,
        level: int,
    ) -> int:
        """
        Calculate experience points for a given level using growth rate formula.

        Args:
            growth_rate: Growth rate object containing formula
            level: Pokemon level

        Returns:
            Experience points required for the level
        """
        if not growth_rate or not growth_rate.formula:
            # Default formula: x^3 (Slow growth rate)
            return int(level**3)

        # Parse and evaluate the formula
        # Common formulas: x^3, x^2, x, etc.
        formula = growth_rate.formula.replace('x', str(level))

        try:
            experience = eval(formula)  # noqa: S307
            return max(0, int(experience))
        except Exception:
            # Fallback to default formula if evaluation fails
            return int(level**3)
