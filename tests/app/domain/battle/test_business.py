import random
from dataclasses import replace

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
