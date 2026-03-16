import ast
import math
import operator as op
import random
from typing import Optional

from app.domain.battle.schema import AttackResult, BattleSchema
from app.domain.pokemon.model import Pokemon
from app.domain.progression.schema import ProgressionListResult, ProgressionResult, StatBlock
from app.shared.utils.number import calculate_by_formula


class PokemonProgressionBusiness:
    XP_MULTIPLIER = 7
    LEVEL_XP_FACTOR = 100
    MAX_TOTAL_EV = 510
    MAX_EV_PER_STAT = 252

    ALLOWED_OPERATORS = {
        ast.Add: op.add,
        ast.Sub: op.sub,
        ast.Mult: op.mul,
        ast.Div: op.truediv,
        ast.Pow: op.pow,
        ast.USub: op.neg,
    }

    @staticmethod
    def initialize_stats(
        pokemon: Optional[Pokemon] = None, level: int = 1
    ) -> ProgressionResult:
        if not pokemon:
            return PokemonProgressionBusiness._return_empty_progression_result()
        growth_rate = pokemon.growth_rate

        if not growth_rate:
            return PokemonProgressionBusiness._return_empty_progression_result()

        formula = growth_rate.formula

        stats_evs = PokemonProgressionBusiness._calculate_evs()
        stats_ivs = PokemonProgressionBusiness._calculate_ivs()
        hp = PokemonProgressionBusiness._calculate_hp(
            hp=pokemon.hp,
            iv_hp=stats_ivs.hp,
            ev_hp=stats_evs.hp,
            level=level,
        )

        return PokemonProgressionBusiness._calculate_stats(
            stats_schema=BattleSchema(
                id='',
                hp=hp,
                wins=0,
                level=level,
                iv_hp=stats_ivs.hp,
                ev_hp=stats_evs.hp,
                losses=0,
                max_hp=hp,
                battles=0,
                nickname=pokemon.name,
                speed=pokemon.speed,
                iv_speed=stats_ivs.speed,
                ev_speed=stats_evs.speed,
                attack=pokemon.attack,
                iv_attack=stats_ivs.attack,
                ev_attack=stats_evs.attack,
                defense=pokemon.defense,
                iv_defense=stats_ivs.defense,
                ev_defense=stats_evs.defense,
                experience=0,
                special_attack=pokemon.special_attack,
                iv_special_attack=stats_ivs.special_attack,
                ev_special_attack=stats_evs.special_attack,
                special_defense=pokemon.special_defense,
                iv_special_defense=stats_ivs.special_defense,
                ev_special_defense=stats_evs.special_defense,
                pokemon=pokemon,
                formula=formula,
            )
        )

    @staticmethod
    def apply_attack_result(
        attacker: BattleSchema, defender: BattleSchema, attack_result: AttackResult
    ) -> ProgressionListResult:
        print(f'# => attack_result => {attack_result}')
        # 1️⃣ Atualizar HP do defensor
        new_defender_hp = max(defender.hp - attack_result.damage, 0)

        level_up = False
        attacker_level = attacker.level
        attacker_wins = attacker.wins
        attacker_experience = attacker.experience

        old_level = attacker_level

        # 2️⃣ Se desmaiou → calcular XP
        if attack_result.fainted:
            xp_gained = PokemonProgressionBusiness._calculate_experience(
                level=defender.level,
                base_experience=defender.pokemon.base_experience,
            )

            attacker_experience = attacker.experience + xp_gained

            new_level = PokemonProgressionBusiness._level_from_experience(
                experience=attacker_experience,
                formula=attacker.formula,
                current_level=attacker.level,
            )

            print(f'# => old_level => {old_level}')
            print(f'# => new_level => {new_level}')

            attacker_wins = attacker.wins + 1

            if new_level > old_level:
                level_up = True
                attacker_level = int(new_level)

        attacker_merged = attacker.model_copy(
            update={
                'level': attacker_level,
                'wins': attacker_wins,
                'experience': attacker_experience,
            }
        )
        attacker_progression_result = PokemonProgressionBusiness._calculate_stats(
            stats_schema=attacker_merged
        )

        defender_merged = defender.model_copy(
            update={
                'hp': new_defender_hp,
            }
        )
        defender_progression_result = PokemonProgressionBusiness._calculate_stats(
            stats_schema=defender_merged
        )
        return ProgressionListResult(
            level_up=level_up,
            attacker_progression=attacker_progression_result,
            defender_progression=defender_progression_result,
        )

    @staticmethod
    def _calculate_stats(
        stats_schema: BattleSchema,
    ) -> ProgressionResult:

        level = stats_schema.level
        pokemon = stats_schema.pokemon
        speed = pokemon.speed
        attack = pokemon.attack
        defense = pokemon.defense
        special_defense = pokemon.special_defense
        special_attack = pokemon.special_attack

        print('# => SPEEED')
        speed_calculated = PokemonProgressionBusiness._calculate_stat(
            level=level,
            iv_stat=stats_schema.iv_speed,
            ev_stat=stats_schema.ev_speed,
            base_stat=speed,
        )

        print('ATTACK')
        attack_calculated = PokemonProgressionBusiness._calculate_stat(
            level=level,
            iv_stat=stats_schema.iv_attack,
            ev_stat=stats_schema.ev_attack,
            base_stat=attack,
        )

        print('DEFENSE')
        defense_calculated = PokemonProgressionBusiness._calculate_stat(
            level=level,
            iv_stat=stats_schema.iv_defense,
            ev_stat=stats_schema.ev_defense,
            base_stat=defense,
        )

        print('SPECIAL ATTACK')
        special_attack_calculated = PokemonProgressionBusiness._calculate_stat(
            level=level,
            iv_stat=stats_schema.iv_special_attack,
            ev_stat=stats_schema.ev_special_attack,
            base_stat=special_attack,
        )

        print('SPECIAL DEFENSE')
        special_defense_calculated = PokemonProgressionBusiness._calculate_stat(
            level=level,
            iv_stat=stats_schema.iv_special_defense,
            ev_stat=stats_schema.ev_special_defense,
            base_stat=special_defense,
        )

        return ProgressionResult(
            hp=stats_schema.hp,
            iv_hp=stats_schema.iv_hp,
            ev_hp=stats_schema.ev_hp,
            max_hp=stats_schema.max_hp,
            wins=stats_schema.wins,
            level=level,
            formula=stats_schema.formula,
            speed=speed_calculated,
            iv_speed=stats_schema.iv_speed,
            ev_speed=stats_schema.ev_speed,
            attack=attack_calculated,
            iv_attack=stats_schema.iv_attack,
            ev_attack=stats_schema.ev_attack,
            losses=0,
            battles=0,
            defense=defense_calculated,
            iv_defense=stats_schema.iv_defense,
            ev_defense=stats_schema.ev_defense,
            experience=stats_schema.experience,
            special_attack=special_attack_calculated,
            iv_special_attack=stats_schema.iv_special_attack,
            ev_special_attack=stats_schema.ev_special_attack,
            special_defense=special_defense_calculated,
            iv_special_defense=stats_schema.iv_special_defense,
            ev_special_defense=stats_schema.ev_special_defense,
        )

    @staticmethod
    def _calculate_hp(
        hp: int,
        iv_hp: int,
        ev_hp: int,
        level: int,
    ) -> int:
        return math.floor(((2 * hp + iv_hp + (ev_hp // 4)) * level) / 100) + level + 10

    @staticmethod
    def _build_base_stats(pokemon: Pokemon) -> StatBlock:
        return StatBlock(
            hp=pokemon.hp or 0,
            speed=pokemon.speed or 0,
            attack=pokemon.attack or 0,
            defense=pokemon.defense or 0,
            special_attack=pokemon.special_attack or 0,
            special_defense=pokemon.special_defense or 0,
        )

    @staticmethod
    def _calculate_stat(
        level: int,  # 1
        iv_stat: int,  # 5
        ev_stat: int,  # 3
        base_stat: int,  # 6
        nature_multiple: float = 1.0,
    ) -> int:
        print('# => _calculate_stat ')
        print(f'# => level => {level}')
        print(f'# => iv_stat => {iv_stat}')
        print(f'# => ev_stat => {ev_stat}')
        print(f'# => base_stat => {base_stat}')
        base_calc = 2 * base_stat + iv_stat + (ev_stat // 4)  # 17.75
        print(f'# => base_calc => {base_calc}')
        scaled = (base_calc * level) / 100  # 0.1775
        print(f'# => scaled => {scaled}')
        stat = math.floor(scaled) + 5  # 5.1775
        print(f'# => stat => {stat}')

        final_stat = math.floor(stat * nature_multiple)
        print(f'# => final_stat => {final_stat}')
        return final_stat

    @staticmethod
    def _calculate_ivs() -> StatBlock:
        return StatBlock(
            hp=random.randint(0, 31),
            speed=random.randint(0, 31),
            attack=random.randint(0, 31),
            defense=random.randint(0, 31),
            special_attack=random.randint(0, 31),
            special_defense=random.randint(0, 31),
        )

    @staticmethod
    def _calculate_evs() -> StatBlock:
        remaining = PokemonProgressionBusiness.MAX_TOTAL_EV
        max_ev_per_stat = PokemonProgressionBusiness.MAX_EV_PER_STAT
        stats = {
            'hp': 0,
            'speed': 0,
            'attack': 0,
            'defense': 0,
            'special_attack': 0,
            'special_defense': 0,
        }

        for stat in stats.keys():
            if remaining <= 0:
                break

            value = random.randint(0, min(max_ev_per_stat, remaining))
            stats[stat] = value
            remaining -= value
        return StatBlock(**stats)

    @staticmethod
    def _calculate_experience(level: int, base_experience: int) -> int:
        return base_experience * max(1, level // PokemonProgressionBusiness.XP_MULTIPLIER)

    @staticmethod
    def _return_empty_progression_result() -> ProgressionResult:
        return ProgressionResult(
            hp=0,
            wins=0,
            level=0,
            speed=0,
            iv_speed=0,
            ev_speed=0,
            attack=0,
            iv_attack=0,
            ev_attack=0,
            max_hp=0,
            losses=0,
            battles=0,
            defense=0,
            iv_defense=0,
            ev_defense=0,
            experience=0,
            special_attack=0,
            iv_special_attack=0,
            ev_special_attack=0,
            special_defense=0,
            iv_special_defense=0,
            ev_special_defense=0,
            iv_hp=0,
            ev_hp=0,
            formula='x',
        )

    @staticmethod
    def _level_from_experience(experience: int, current_level: int, formula: str) -> int:
        """
        Calculate the Pokemon's current level based on experience.

        The method increments the level until finding a level where the
        experience required for that level is greater than the Pokemon's
        current experience. Returns the closest lower level.

        Args:
            experience: The current experience points of the Pokemon.
            current_level: The starting level to check from.
            formula: The growth rate formula to calculate experience required per level.

        Returns:
            The new level based on the experience accumulated.
        """
        level = current_level
        print(f'# => experience => {experience}')
        while True:
            experience_for_next_level = calculate_by_formula(formula, level + 1)
            print(f'# => next_level => {level + 1}')
            print(f'# => experience_for_next_level => {experience_for_next_level}')

            if experience_for_next_level > experience:
                return level

            level += 1
