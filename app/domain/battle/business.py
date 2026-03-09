import random
from typing import Optional

from app.domain.battle.schema import AttackResult, BattleSchema, ValidatPreconditions
from app.domain.captured_pokemon.model import CapturedPokemon
from app.domain.move.model import PokemonMove
from app.domain.pokedex.model import Pokedex


class PokemonBattleBusiness:
    TYPE_CHART = {
        ('fire', 'grass'): 2.0,
        ('water', 'fire'): 2.0,
        ('grass', 'water'): 2.0,
        ('electric', 'water'): 2.0,
        ('fire', 'water'): 0.5,
        ('water', 'grass'): 0.5,
        ('grass', 'fire'): 0.5,
    }
    CRITICAL_CHANCE = 0.0625
    CRITICAL_MULTIPLIER = 1.5
    STAB_MULTIPLIER = 1.5

    @staticmethod
    def execute_attack(
        attacker: BattleSchema, defender: BattleSchema, move: Optional[PokemonMove] = None
    ) -> AttackResult:

        validate = PokemonBattleBusiness._validate_preconditions(attacker, defender, move)

        if validate.error or move is None:
            return PokemonBattleBusiness._build_error_result(
                error_detail=validate.error_detail
            )

        if PokemonBattleBusiness._missed(move.accuracy):
            return PokemonBattleBusiness._build_miss_result(defender.hp)

        # 2 Status Move (não causa dano direto)
        if move.damage_class == 'status':
            return PokemonBattleBusiness._build_status_result(defender.hp, move.name)

        # 3️⃣ Damage calculation
        damage, critical, effectiveness, stab = PokemonBattleBusiness._calculate_damage(
            attacker, defender, move
        )

        remaining_hp = max(defender.hp - damage, 0)

        return AttackResult(
            damage=damage,
            remaining_hp=remaining_hp,
            fainted=remaining_hp == 0,
            critical=critical,
            effectiveness=effectiveness,
            stab=stab,
            missed=False,
        )

    # =========================
    # VALIDATIONS
    # =========================
    @staticmethod
    def _validate_preconditions(
        attacker: BattleSchema, defender: BattleSchema, move: Optional[PokemonMove] = None
    ) -> ValidatPreconditions:
        if not move:
            return ValidatPreconditions(error=True, error_detail='Move not found')

        if not attacker.pokemon or not defender.pokemon:
            return ValidatPreconditions(
                error=True, error_detail='Pokemon data missing for battle.'
            )

        if defender.hp <= 0:
            return ValidatPreconditions(
                error=True, error_detail='Defender Pokémon is fainted.'
            )

        if attacker.hp <= 0:
            return ValidatPreconditions(
                error=True, error_detail='Attacker Pokémon is fainted.'
            )

        if move.pp <= 0:
            return ValidatPreconditions(error=True, error_detail='Move has no PP left.')

        return ValidatPreconditions(error=False, error_detail=None)

    # =========================
    # ACCURACY
    # =========================
    @staticmethod
    def _missed(accuracy: int) -> bool:
        if accuracy <= 0:
            return True

        hit_roll = random.randint(1, 100)
        return hit_roll > accuracy

    # =========================
    # STATUS
    # =========================
    @staticmethod
    def _build_miss_result(defender_hp: int) -> AttackResult:
        return AttackResult(
            damage=0,
            remaining_hp=defender_hp,
            fainted=False,
            critical=False,
            effectiveness=1.0,
            stab=False,
            missed=True,
        )

    @staticmethod
    def _build_error_result(error_detail: Optional[str] = None) -> AttackResult:
        return AttackResult(
            damage=0,
            remaining_hp=0,
            fainted=False,
            critical=False,
            effectiveness=1.0,
            stab=False,
            missed=False,
            error=True,
            error_detail=error_detail,
        )

    @staticmethod
    def _build_status_result(defender_hp: int, status_name: str) -> AttackResult:
        return AttackResult(
            damage=0,
            remaining_hp=defender_hp,
            fainted=False,
            critical=False,
            effectiveness=1.0,
            stab=False,
            missed=False,
            applied_status=status_name,
        )

    # =========================
    # DAMAGE CORE
    # =========================
    @staticmethod
    def _calculate_damage(attacker: BattleSchema, defender: BattleSchema, move: PokemonMove):

        attack_stat, defense_stat = PokemonBattleBusiness._select_stats(
            attacker, defender, move.damage_class
        )

        base_damage = PokemonBattleBusiness._base_damage_formula(
            attacker.level, move.power, attack_stat, defense_stat
        )

        attacker_pokemon = attacker.pokemon
        defender_pokemon = defender.pokemon
        stab = move.type in attacker_pokemon.types
        stab_multiplier = PokemonBattleBusiness.STAB_MULTIPLIER if stab else 1.0

        defender_types = [item.name for item in defender_pokemon.types]
        effectiveness = PokemonBattleBusiness._calculate_effectiveness(
            move.type, defender_types
        )

        if effectiveness == 0:
            return 0, False, 0.0, stab

        critical = random.random() < PokemonBattleBusiness.CRITICAL_CHANCE
        critical_multiplier = PokemonBattleBusiness.CRITICAL_MULTIPLIER if critical else 1.0

        random_multiplier = random.uniform(0.85, 1.0)

        final_damage = int(
            base_damage
            * stab_multiplier
            * effectiveness
            * critical_multiplier
            * random_multiplier
        )

        return final_damage, critical, effectiveness, stab

    # =========================
    # HELPERS
    # =========================

    @staticmethod
    def _select_stats(attacker: BattleSchema, defender: BattleSchema, damage_class: str):
        if damage_class == 'physical':
            return attacker.attack, defender.defense

        if damage_class == 'special':
            return attacker.special_attack, defender.special_defense

        raise ValueError(f'Invalid damage class: {damage_class}')

    @staticmethod
    def _base_damage_formula(level: int, power: int, attack: int, defense: int) -> float:

        return (((2 * level / 5 + 2) * power * attack / defense) / 50) + 2

    @staticmethod
    def _calculate_effectiveness(move_type: str, defender_types: list[str]) -> float:

        effectiveness = 1.0

        for defender_type in defender_types:
            effectiveness *= PokemonBattleBusiness.TYPE_CHART.get(
                (move_type, defender_type), 1.0
            )

        return effectiveness

    @staticmethod
    def convert_captured_pokemon_to_pokemon_stats(
        captured_pokemon: CapturedPokemon,
    ) -> BattleSchema:
        return BattleSchema(
            id=captured_pokemon.id,
            hp=captured_pokemon.hp,
            wins=captured_pokemon.wins,
            level=captured_pokemon.level,
            iv_hp=captured_pokemon.iv_hp,
            ev_hp=captured_pokemon.ev_hp,
            losses=captured_pokemon.losses,
            max_hp=captured_pokemon.max_hp,
            battles=captured_pokemon.battles,
            nickname=captured_pokemon.nickname,
            speed=captured_pokemon.speed,
            iv_speed=captured_pokemon.iv_speed,
            ev_speed=captured_pokemon.ev_speed,
            attack=captured_pokemon.attack,
            iv_attack=captured_pokemon.iv_attack,
            ev_attack=captured_pokemon.ev_attack,
            defense=captured_pokemon.defense,
            iv_defense=captured_pokemon.iv_defense,
            ev_defense=captured_pokemon.ev_defense,
            experience=captured_pokemon.experience,
            special_attack=captured_pokemon.special_attack,
            iv_special_attack=captured_pokemon.iv_special_attack,
            ev_special_attack=captured_pokemon.ev_special_attack,
            special_defense=captured_pokemon.special_defense,
            iv_special_defense=captured_pokemon.iv_special_defense,
            ev_special_defense=captured_pokemon.ev_special_defense,
            pokemon=captured_pokemon.pokemon,
            formula=captured_pokemon.formula,
        )

    @staticmethod
    def convert_pokedex_to_pokemon_stats(pokedex: Pokedex) -> BattleSchema:
        return BattleSchema(
            id=pokedex.id,
            hp=pokedex.hp,
            wins=pokedex.wins,
            level=pokedex.level,
            iv_hp=pokedex.iv_hp,
            ev_hp=pokedex.ev_hp,
            losses=pokedex.losses,
            max_hp=pokedex.max_hp,
            battles=pokedex.battles,
            nickname=pokedex.nickname,
            speed=pokedex.speed,
            iv_speed=pokedex.iv_speed,
            ev_speed=pokedex.ev_speed,
            attack=pokedex.attack,
            iv_attack=pokedex.iv_attack,
            ev_attack=pokedex.ev_attack,
            defense=pokedex.defense,
            iv_defense=pokedex.iv_defense,
            ev_defense=pokedex.ev_defense,
            experience=pokedex.experience,
            special_attack=pokedex.special_attack,
            iv_special_attack=pokedex.iv_special_attack,
            ev_special_attack=pokedex.ev_special_attack,
            special_defense=pokedex.special_defense,
            iv_special_defense=pokedex.iv_special_defense,
            ev_special_defense=pokedex.ev_special_defense,
            pokemon=pokedex.pokemon,
            formula=pokedex.formula,
        )
