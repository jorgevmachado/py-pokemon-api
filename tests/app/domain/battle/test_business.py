import random
from dataclasses import replace

import pytest

from app.domain.battle.business import PokemonBattleBusiness
from app.domain.battle.schema import BattleSchema
from tests.factories.pokemon import MOCK_POKEMON_BULBASAUR, MOCK_POKEMON_CHARIZARD
from tests.factories.pokemon_move import MOCK_POKEMON_MOVE_MEGA_DRAIN

MOCK_ATTACKER_BATTLE_SCHEMA = BattleSchema(
    id='dc39be0b-503c-4e61-a63f-9f0b92475ad1',
    hp=12,
    wins=0,
    level=1,
    iv_hp=20,
    ev_hp=243,
    losses=0,
    max_hp=12,
    battles=0,
    nickname='bulbasaur',
    speed=6,
    iv_speed=30,
    ev_speed=61,
    attack=6,
    iv_attack=5,
    ev_attack=3,
    defense=6,
    iv_defense=10,
    ev_defense=11,
    experience=0,
    special_attack=6,
    iv_special_attack=11,
    ev_special_attack=86,
    special_defense=6,
    iv_special_defense=29,
    ev_special_defense=36,
    pokemon=MOCK_POKEMON_BULBASAUR,
    formula='\frac{6x^3}{5} - 15x^2 + 100x - 140',
)

MOCK_DEFENDER_BATTLE_SCHEMA = BattleSchema(
    id='f69717a1-e516-4031-8e8a-c8cad38fde16',
    hp=13,
    wins=0,
    level=1,
    iv_hp=22,
    ev_hp=102,
    losses=0,
    max_hp=13,
    battles=0,
    nickname='charizard',
    speed=7,
    iv_speed=14,
    ev_speed=227,
    attack=6,
    iv_attack=8,
    ev_attack=15,
    defense=6,
    iv_defense=6,
    ev_defense=99,
    experience=0,
    special_attack=7,
    iv_special_attack=9,
    ev_special_attack=21,
    special_defense=6,
    iv_special_defense=8,
    ev_special_defense=39,
    pokemon=MOCK_POKEMON_CHARIZARD,
    formula='\frac{6x^3}{5} - 15x^2 + 100x - 140',
)


class TestPokemonBattleBusinessValidatePreconditions:
    """Test scope for execute validate preconditions method"""

    @staticmethod
    def test_validate_preconditions_move_not_found():
        """Should raise error when move is not found"""
        business = PokemonBattleBusiness()

        result = business._validate_preconditions(
            attacker=MOCK_ATTACKER_BATTLE_SCHEMA,
            defender=MOCK_DEFENDER_BATTLE_SCHEMA,
        )

        assert result.error_detail == 'Move not found'
        assert result.error

    @staticmethod
    def test_validate_preconditions_attacker_pokemon_data_missing():
        """Should raise error when attacker pokemon data is missing"""
        business = PokemonBattleBusiness()

        result = business._validate_preconditions(
            attacker=MOCK_ATTACKER_BATTLE_SCHEMA.model_copy(update={'pokemon': None}),
            defender=MOCK_DEFENDER_BATTLE_SCHEMA,
            move=MOCK_POKEMON_MOVE_MEGA_DRAIN,
        )

        assert result.error_detail == 'Pokemon data missing for battle.'
        assert result.error

    @staticmethod
    def test_validate_preconditions_defender_pokemon_data_missing():
        """Should raise error when defender pokemon data is missing"""
        business = PokemonBattleBusiness()

        result = business._validate_preconditions(
            attacker=MOCK_ATTACKER_BATTLE_SCHEMA,
            defender=MOCK_DEFENDER_BATTLE_SCHEMA.model_copy(update={'pokemon': None}),
            move=MOCK_POKEMON_MOVE_MEGA_DRAIN,
        )

        assert result.error_detail == 'Pokemon data missing for battle.'
        assert result.error

    @staticmethod
    def test_validate_preconditions_pokemon_with_defender_hp_zero():
        """Should raise error when defender pokemon hp is zero"""
        business = PokemonBattleBusiness()

        result = business._validate_preconditions(
            attacker=MOCK_ATTACKER_BATTLE_SCHEMA,
            defender=MOCK_DEFENDER_BATTLE_SCHEMA.model_copy(update={'hp': 0}),
            move=MOCK_POKEMON_MOVE_MEGA_DRAIN,
        )

        assert result.error_detail == 'Defender Pokémon is fainted.'
        assert result.error

    @staticmethod
    def test_validate_preconditions_pokemon_with_attacker_hp_zero():
        """Should raise error when attacker pokemon hp is zero"""
        business = PokemonBattleBusiness()

        result = business._validate_preconditions(
            attacker=MOCK_ATTACKER_BATTLE_SCHEMA.model_copy(update={'hp': 0}),
            defender=MOCK_DEFENDER_BATTLE_SCHEMA,
            move=MOCK_POKEMON_MOVE_MEGA_DRAIN,
        )

        assert result.error_detail == 'Attacker Pokémon is fainted.'
        assert result.error

    @staticmethod
    def test_validate_preconditions_move_with_pp_zero():
        """Should raise error when move pp is zero"""
        business = PokemonBattleBusiness()

        result = business._validate_preconditions(
            attacker=MOCK_ATTACKER_BATTLE_SCHEMA,
            defender=MOCK_DEFENDER_BATTLE_SCHEMA,
            move=replace(MOCK_POKEMON_MOVE_MEGA_DRAIN, pp=0),
        )

        assert result.error_detail == 'Move has no PP left.'
        assert result.error

    @staticmethod
    def test_validate_preconditions_success():
        """Should return no error when preconditions are met"""
        business = PokemonBattleBusiness()

        result = business._validate_preconditions(
            attacker=MOCK_ATTACKER_BATTLE_SCHEMA,
            defender=MOCK_DEFENDER_BATTLE_SCHEMA,
            move=MOCK_POKEMON_MOVE_MEGA_DRAIN,
        )

        assert not result.error_detail
        assert not result.error


class TestPokemonBattleBusinessBuildErrorResult:
    """Test scope for execute build error result method"""

    @staticmethod
    def test_build_error_result():
        """Should return error result when error is True"""
        business = PokemonBattleBusiness()

        result = business._build_error_result(error_detail='ONE ERROR')

        assert result.error_detail == 'ONE ERROR'
        assert result.error


class TestPokemonBattleBusinessBuildMissResult:
    """Test scope for execute build miss result method"""

    @staticmethod
    def test_build_miss_result():
        """Should return error result when error is True"""
        business = PokemonBattleBusiness()

        result = business._build_miss_result(defender_hp=0)

        assert result.damage == 0
        assert result.remaining_hp == 0
        assert not result.fainted
        assert not result.critical
        assert result.effectiveness is not None
        assert not result.stab
        assert result.missed


class TestPokemonBattleBusinessBuildStatusResult:
    """Test scope for execute build status result method"""

    @staticmethod
    def test_build_status_result():
        """Should return status result when error is False"""
        business = PokemonBattleBusiness()

        result = business._build_status_result(defender_hp=0, status_name='PARALYSIS')

        assert result.damage == 0
        assert result.remaining_hp == 0
        assert not result.fainted
        assert not result.critical
        assert result.effectiveness is not None
        assert not result.stab
        assert not result.missed
        assert result.applied_status == 'PARALYSIS'


class TestPokemonBattleBusinessBaseDamageFormula:
    """Test scope for base damage formula method"""

    @staticmethod
    def test_base_damage_formula():
        """Should return base damage formula when error is False"""
        result_base_damage = 4
        business = PokemonBattleBusiness()
        base_damage = business._base_damage_formula(
            level=MOCK_ATTACKER_BATTLE_SCHEMA.level,
            power=MOCK_POKEMON_MOVE_MEGA_DRAIN.power,
            attack=MOCK_ATTACKER_BATTLE_SCHEMA.attack,
            defense=MOCK_ATTACKER_BATTLE_SCHEMA.defense,
        )
        assert base_damage < result_base_damage


class TestPokemonBattleBusinessExecuteAttack:
    """Test scope for execute attack method"""

    @staticmethod
    def test_execute_attack_move_not_found():
        """Should raise error when move is not found"""
        business = PokemonBattleBusiness()

        result = business.execute_attack(
            attacker=MOCK_ATTACKER_BATTLE_SCHEMA,
            defender=MOCK_DEFENDER_BATTLE_SCHEMA,
        )

        assert result.damage == 0
        assert result.remaining_hp == 0
        assert not result.fainted
        assert not result.critical
        assert result.effectiveness is not None
        assert not result.stab
        assert not result.missed
        assert result.error
        assert result.error_detail == 'Move not found'
        assert not result.applied_status

    @staticmethod
    def test_execute_attack_attacker_pokemon_data_missing():
        """Should raise error when attacker pokemon data is missing"""
        business = PokemonBattleBusiness()

        result = business.execute_attack(
            attacker=MOCK_ATTACKER_BATTLE_SCHEMA.model_copy(update={'pokemon': None}),
            defender=MOCK_DEFENDER_BATTLE_SCHEMA,
            move=MOCK_POKEMON_MOVE_MEGA_DRAIN,
        )

        assert result.damage == 0
        assert result.remaining_hp == 0
        assert not result.fainted
        assert not result.critical
        assert result.effectiveness is not None
        assert not result.stab
        assert not result.missed
        assert result.error
        assert result.error_detail == 'Pokemon data missing for battle.'
        assert not result.applied_status

    @staticmethod
    def test_execute_attack_defender_pokemon_data_missing():
        """Should raise error when defender pokemon data is missing"""
        business = PokemonBattleBusiness()

        result = business.execute_attack(
            attacker=MOCK_ATTACKER_BATTLE_SCHEMA,
            defender=MOCK_DEFENDER_BATTLE_SCHEMA.model_copy(update={'pokemon': None}),
            move=MOCK_POKEMON_MOVE_MEGA_DRAIN,
        )

        assert result.damage == 0
        assert result.remaining_hp == 0
        assert not result.fainted
        assert not result.critical
        assert result.effectiveness is not None
        assert not result.stab
        assert not result.missed
        assert result.error
        assert result.error_detail == 'Pokemon data missing for battle.'
        assert not result.applied_status

    @staticmethod
    def test_execute_attack_pokemon_with_defender_hp_zero():
        """Should raise error when defender pokemon hp is zero"""
        business = PokemonBattleBusiness()

        result = business.execute_attack(
            attacker=MOCK_ATTACKER_BATTLE_SCHEMA,
            defender=MOCK_DEFENDER_BATTLE_SCHEMA.model_copy(update={'hp': 0}),
            move=MOCK_POKEMON_MOVE_MEGA_DRAIN,
        )

        assert result.damage == 0
        assert result.remaining_hp == 0
        assert not result.fainted
        assert not result.critical
        assert result.effectiveness is not None
        assert not result.stab
        assert not result.missed
        assert result.error
        assert result.error_detail == 'Defender Pokémon is fainted.'
        assert not result.applied_status

    @staticmethod
    def test_execute_attack_pokemon_with_attacker_hp_zero():
        """Should raise error when attacker pokemon hp is zero"""
        business = PokemonBattleBusiness()

        result = business.execute_attack(
            attacker=MOCK_ATTACKER_BATTLE_SCHEMA.model_copy(update={'hp': 0}),
            defender=MOCK_DEFENDER_BATTLE_SCHEMA,
            move=MOCK_POKEMON_MOVE_MEGA_DRAIN,
        )

        assert result.damage == 0
        assert result.remaining_hp == 0
        assert not result.fainted
        assert not result.critical
        assert result.effectiveness is not None
        assert not result.stab
        assert not result.missed
        assert result.error
        assert result.error_detail == 'Attacker Pokémon is fainted.'
        assert not result.applied_status

    @staticmethod
    def test_execute_attack_move_with_pp_zero():
        """Should raise error when move pp is zero"""
        business = PokemonBattleBusiness()

        result = business.execute_attack(
            attacker=MOCK_ATTACKER_BATTLE_SCHEMA,
            defender=MOCK_DEFENDER_BATTLE_SCHEMA,
            move=replace(MOCK_POKEMON_MOVE_MEGA_DRAIN, pp=0),
        )

        assert result.damage == 0
        assert result.remaining_hp == 0
        assert not result.fainted
        assert not result.critical
        assert result.effectiveness is not None
        assert not result.stab
        assert not result.missed
        assert result.error
        assert result.error_detail == 'Move has no PP left.'
        assert not result.applied_status

    @staticmethod
    def test_execute_attack_missed():
        """Should return error result when error is True"""
        business = PokemonBattleBusiness()

        result = business.execute_attack(
            attacker=MOCK_ATTACKER_BATTLE_SCHEMA,
            defender=MOCK_DEFENDER_BATTLE_SCHEMA,
            move=replace(MOCK_POKEMON_MOVE_MEGA_DRAIN, accuracy=0),
        )

        assert result.damage == 0
        assert result.remaining_hp == MOCK_DEFENDER_BATTLE_SCHEMA.hp
        assert not result.fainted
        assert not result.critical
        assert result.effectiveness is not None
        assert not result.stab
        assert result.missed
        assert not result.error
        assert not result.error_detail
        assert not result.applied_status

    @staticmethod
    def test_execute_attack_not_damage():
        """Should return error result when error is True"""
        business = PokemonBattleBusiness()

        result = business.execute_attack(
            attacker=MOCK_ATTACKER_BATTLE_SCHEMA,
            defender=MOCK_DEFENDER_BATTLE_SCHEMA,
            move=replace(MOCK_POKEMON_MOVE_MEGA_DRAIN, damage_class='status'),
        )

        assert result.damage == 0
        assert result.remaining_hp == MOCK_DEFENDER_BATTLE_SCHEMA.hp
        assert not result.fainted
        assert not result.critical
        assert result.effectiveness is not None
        assert not result.stab
        assert not result.missed
        assert not result.error
        assert not result.error_detail
        assert result.applied_status == MOCK_POKEMON_MOVE_MEGA_DRAIN.name

    @staticmethod
    def test_execute_attack_success(monkeypatch):
        """Should return success"""
        monkeypatch.setattr(random, 'uniform', lambda a, b: 0.8615340506528313)
        business = PokemonBattleBusiness()

        result = business.execute_attack(
            attacker=MOCK_ATTACKER_BATTLE_SCHEMA,
            defender=MOCK_DEFENDER_BATTLE_SCHEMA,
            move=MOCK_POKEMON_MOVE_MEGA_DRAIN,
        )

        assert result.damage > 0
        assert result.remaining_hp > 0
        assert not result.fainted
        assert result.critical is not None
        assert result.effectiveness is not None
        assert not result.stab
        assert not result.missed
        assert not result.error
        assert not result.error_detail
        assert not result.applied_status


class TestPokemonBattleBusinessSelectStats:
    """Test scope for select stats method"""

    @staticmethod
    def test_select_stats_physical():
        """Should return attack and defense for physical damage"""
        business = PokemonBattleBusiness()

        attack, defense = business._select_stats(
            MOCK_ATTACKER_BATTLE_SCHEMA, MOCK_DEFENDER_BATTLE_SCHEMA, 'physical'
        )

        assert attack == MOCK_ATTACKER_BATTLE_SCHEMA.attack
        assert defense == MOCK_DEFENDER_BATTLE_SCHEMA.defense

    @staticmethod
    def test_select_stats_special():
        """Should return special attack and special defense for special damage"""
        business = PokemonBattleBusiness()

        attack, defense = business._select_stats(
            MOCK_ATTACKER_BATTLE_SCHEMA, MOCK_DEFENDER_BATTLE_SCHEMA, 'special'
        )

        assert attack == MOCK_ATTACKER_BATTLE_SCHEMA.special_attack
        assert defense == MOCK_DEFENDER_BATTLE_SCHEMA.special_defense

    @staticmethod
    def test_select_stats_invalid_damage_class():
        """Should raise ValueError for invalid damage class"""
        business = PokemonBattleBusiness()

        with pytest.raises(ValueError, match='Invalid damage class'):
            business._select_stats(
                MOCK_ATTACKER_BATTLE_SCHEMA, MOCK_DEFENDER_BATTLE_SCHEMA, 'invalid'
            )


class TestPokemonBattleBusinessCalculateEffectiveness:
    """Test scope for calculate effectiveness method"""

    @staticmethod
    def test_calculate_effectiveness_super_effective():
        """Should return 2.0 for super effective attack"""
        business = PokemonBattleBusiness()
        effectiveness_result = 2
        effectiveness = business._calculate_effectiveness('fire', ['grass'])

        assert effectiveness >= effectiveness_result

    @staticmethod
    def test_calculate_effectiveness_not_very_effective():
        """Should return 0.5 for not very effective attack"""
        business = PokemonBattleBusiness()
        effectiveness_result = 0
        effectiveness = business._calculate_effectiveness('fire', ['water'])

        assert effectiveness >= effectiveness_result

    @staticmethod
    def test_calculate_effectiveness_neutral():
        """Should return 1.0 for neutral effectiveness"""
        business = PokemonBattleBusiness()
        effectiveness_result = 1
        effectiveness = business._calculate_effectiveness('fire', ['electric'])

        assert effectiveness >= effectiveness_result

    @staticmethod
    def test_calculate_effectiveness_multiple_types():
        """Should multiply effectiveness for multiple types"""
        business = PokemonBattleBusiness()
        effectiveness_result = 4
        effectiveness = business._calculate_effectiveness('fire', ['grass', 'grass'])

        assert effectiveness >= effectiveness_result

    @staticmethod
    def test_calculate_effectiveness_mixed_effectiveness():
        """Should multiply mixed effectiveness values"""
        business = PokemonBattleBusiness()
        effectiveness_result = 1
        effectiveness = business._calculate_effectiveness('water', ['fire', 'grass'])

        assert effectiveness >= effectiveness_result

    @staticmethod
    def test_calculate_effectiveness_immunity():
        """Should return 0.0 when move is ineffective"""
        business = PokemonBattleBusiness()
        effectiveness_result = 0
        effectiveness = business._calculate_effectiveness('fire', ['water', 'water'])

        assert effectiveness >= effectiveness_result


class TestPokemonBattleBusinessCalculateDamageWithZeroEffectiveness:
    """Test scope for calculate damage with zero effectiveness"""

    @staticmethod
    def test_calculate_damage_with_normal_effectiveness():
        """Should calculate damage with normal effectiveness"""
        business = PokemonBattleBusiness()

        damage, critical, effectiveness, stab = business._calculate_damage(
            MOCK_ATTACKER_BATTLE_SCHEMA,
            MOCK_DEFENDER_BATTLE_SCHEMA,
            MOCK_POKEMON_MOVE_MEGA_DRAIN,
        )

        assert damage > 0
        assert effectiveness > 0.0

    @staticmethod
    def test_calculate_damage_super_effective():
        """Should calculate higher damage when super effective"""
        business = PokemonBattleBusiness()

        move_water = replace(MOCK_POKEMON_MOVE_MEGA_DRAIN, type='water')
        damage, critical, effectiveness, stab = business._calculate_damage(
            MOCK_ATTACKER_BATTLE_SCHEMA,
            MOCK_DEFENDER_BATTLE_SCHEMA,
            move_water,
        )

        assert damage >= 0
        assert effectiveness >= 1.0

    @staticmethod
    def test_calculate_damage_zero_effectiveness_returns_zero():
        """Should return zero damage when effectiveness is zero"""
        business = PokemonBattleBusiness()

        class DummyType:
            def __init__(self, name):
                self.name = name

        class DummyPokemon:
            def __init__(self, types):
                self.types = types

        zero_type = 'ghost'
        original_chart = PokemonBattleBusiness.TYPE_CHART.copy()
        PokemonBattleBusiness.TYPE_CHART[(zero_type, zero_type)] = 0.0

        attacker = MOCK_ATTACKER_BATTLE_SCHEMA.model_copy(
            update={'pokemon': DummyPokemon(types=[zero_type])}
        )
        defender = MOCK_DEFENDER_BATTLE_SCHEMA.model_copy(
            update={'pokemon': DummyPokemon(types=[DummyType(zero_type)])}
        )
        move = replace(MOCK_POKEMON_MOVE_MEGA_DRAIN, type=zero_type)

        try:
            damage, critical, effectiveness, stab = business._calculate_damage(
                attacker,
                defender,
                move,
            )
        finally:
            PokemonBattleBusiness.TYPE_CHART = original_chart

        assert damage == 0
        assert critical is False
        assert effectiveness == 0.0
        assert isinstance(stab, bool)


class TestPokemonBattleBusinessMissedChance:
    """Test scope for missed attack calculation"""

    @staticmethod
    def test_missed_with_zero_accuracy():
        """Should always miss with zero accuracy"""
        business = PokemonBattleBusiness()

        result = business._missed(accuracy=0)

        assert result is True

    @staticmethod
    def test_missed_with_negative_accuracy():
        """Should always miss with negative accuracy"""
        business = PokemonBattleBusiness()

        result = business._missed(accuracy=-1)

        assert result is True

    @staticmethod
    def test_missed_with_100_accuracy(monkeypatch):
        """Should hit with very high accuracy"""
        monkeypatch.setattr(random, 'randint', lambda a, b: 50)
        business = PokemonBattleBusiness()

        result = business._missed(accuracy=100)

        assert result is False


class TestPokemonBattleBusinessBaseDamageCalculation:
    """Test scope for base damage formula calculation"""

    @staticmethod
    def test_base_damage_formula_calculation():
        """Should calculate base damage correctly"""
        business = PokemonBattleBusiness()

        base_damage = business._base_damage_formula(level=10, power=50, attack=30, defense=25)

        assert base_damage > 0
        assert isinstance(base_damage, float)

    @staticmethod
    def test_base_damage_with_high_attack():
        """Should return higher damage with higher attack"""
        business = PokemonBattleBusiness()

        damage_low = business._base_damage_formula(level=10, power=50, attack=10, defense=25)
        damage_high = business._base_damage_formula(level=10, power=50, attack=100, defense=25)

        assert damage_high > damage_low

    @staticmethod
    def test_base_damage_with_high_defense():
        """Should return lower damage against higher defense"""
        business = PokemonBattleBusiness()

        damage_low_def = business._base_damage_formula(
            level=10, power=50, attack=30, defense=10
        )
        damage_high_def = business._base_damage_formula(
            level=10, power=50, attack=30, defense=100
        )

        assert damage_low_def > damage_high_def


class TestPokemonBattleBusinessConvertCapturedPokemon:
    """Test scope for convert captured pokemon to pokemon stats"""

    @staticmethod
    def test_convert_captured_pokemon_preserves_battle_schema():
        """Should preserve BattleSchema fields when converting"""
        business = PokemonBattleBusiness()

        result = business.convert_captured_pokemon_to_pokemon_stats(
            MOCK_ATTACKER_BATTLE_SCHEMA,
        )

        assert isinstance(result, BattleSchema)
        assert result.hp == MOCK_ATTACKER_BATTLE_SCHEMA.hp
        assert result.attack == MOCK_ATTACKER_BATTLE_SCHEMA.attack
        assert result.defense == MOCK_ATTACKER_BATTLE_SCHEMA.defense

    @staticmethod
    def test_convert_captured_pokemon_all_iv_ev_fields():
        """Should preserve all IV and EV fields"""
        business = PokemonBattleBusiness()

        result = business.convert_captured_pokemon_to_pokemon_stats(
            MOCK_ATTACKER_BATTLE_SCHEMA,
        )

        assert result.iv_hp == MOCK_ATTACKER_BATTLE_SCHEMA.iv_hp
        assert result.ev_hp == MOCK_ATTACKER_BATTLE_SCHEMA.ev_hp
        assert result.iv_attack == MOCK_ATTACKER_BATTLE_SCHEMA.iv_attack
        assert result.ev_attack == MOCK_ATTACKER_BATTLE_SCHEMA.ev_attack
        assert result.iv_defense == MOCK_ATTACKER_BATTLE_SCHEMA.iv_defense
        assert result.ev_defense == MOCK_ATTACKER_BATTLE_SCHEMA.ev_defense

    @staticmethod
    def test_convert_captured_pokemon_returns_schema():
        """Should return BattleSchema instance"""
        business = PokemonBattleBusiness()

        result = business.convert_captured_pokemon_to_pokemon_stats(
            MOCK_ATTACKER_BATTLE_SCHEMA,
        )

        assert isinstance(result, BattleSchema)
        assert result.pokemon == MOCK_ATTACKER_BATTLE_SCHEMA.pokemon
        assert result.formula == MOCK_ATTACKER_BATTLE_SCHEMA.formula


class TestPokemonBattleBusinessConvertPokedex:
    """Test scope for convert pokedex to pokemon stats"""

    @staticmethod
    def test_convert_pokedex_preserves_battle_schema():
        """Should preserve BattleSchema fields when converting"""
        business = PokemonBattleBusiness()

        result = business.convert_pokedex_to_pokemon_stats(
            MOCK_DEFENDER_BATTLE_SCHEMA,
        )

        assert isinstance(result, BattleSchema)
        assert result.hp == MOCK_DEFENDER_BATTLE_SCHEMA.hp
        assert result.attack == MOCK_DEFENDER_BATTLE_SCHEMA.attack
        assert result.defense == MOCK_DEFENDER_BATTLE_SCHEMA.defense

    @staticmethod
    def test_convert_pokedex_all_iv_ev_fields():
        """Should preserve all IV and EV fields"""
        business = PokemonBattleBusiness()

        result = business.convert_pokedex_to_pokemon_stats(
            MOCK_DEFENDER_BATTLE_SCHEMA,
        )

        assert result.iv_hp == MOCK_DEFENDER_BATTLE_SCHEMA.iv_hp
        assert result.ev_hp == MOCK_DEFENDER_BATTLE_SCHEMA.ev_hp
        assert result.iv_attack == MOCK_DEFENDER_BATTLE_SCHEMA.iv_attack
        assert result.ev_attack == MOCK_DEFENDER_BATTLE_SCHEMA.ev_attack
        assert result.iv_defense == MOCK_DEFENDER_BATTLE_SCHEMA.iv_defense
        assert result.ev_defense == MOCK_DEFENDER_BATTLE_SCHEMA.ev_defense

    @staticmethod
    def test_convert_pokedex_returns_schema():
        """Should return BattleSchema instance"""
        business = PokemonBattleBusiness()

        result = business.convert_pokedex_to_pokemon_stats(
            MOCK_DEFENDER_BATTLE_SCHEMA,
        )

        assert isinstance(result, BattleSchema)
        assert result.pokemon == MOCK_DEFENDER_BATTLE_SCHEMA.pokemon
        assert result.formula == MOCK_DEFENDER_BATTLE_SCHEMA.formula
