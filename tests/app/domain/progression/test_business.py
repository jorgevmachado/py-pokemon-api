from app.domain.battle.schema import AttackResult, BattleSchema
from app.domain.progression.business import PokemonProgressionBusiness
from app.domain.progression.schema import ProgressionResult, StatBlock
from tests.factories.growth_rate import PokemonGrowthRateFactory
from tests.factories.pokemon import PokemonFactory

MIN_IV_EV = 0
MAX_IV = 31
MAX_EV = 255

ATTACK_DAMAGE = 5
BASE_EXPERIENCE = 50
FORMULA_SIMPLE = 'x*10'
LEVEL_START = 1
LEVEL_AFTER_XP = 5
LEVEL_HIGH = 14
ZERO_VALUE = 0
HP_BASE = 10
HP_EXPECTED = 11
ATTACKER_HP = 20
DEFENDER_HP = 10


def build_battle_schema(*, level, hp, pokemon, formula):
    return BattleSchema(
        id='battle-id',
        hp=hp,
        wins=0,
        level=level,
        iv_hp=ZERO_VALUE,
        ev_hp=ZERO_VALUE,
        losses=0,
        max_hp=hp,
        battles=0,
        nickname=pokemon.name,
        speed=pokemon.speed,
        iv_speed=ZERO_VALUE,
        ev_speed=ZERO_VALUE,
        attack=pokemon.attack,
        iv_attack=ZERO_VALUE,
        ev_attack=ZERO_VALUE,
        defense=pokemon.defense,
        iv_defense=ZERO_VALUE,
        ev_defense=ZERO_VALUE,
        experience=ZERO_VALUE,
        special_attack=pokemon.special_attack,
        iv_special_attack=ZERO_VALUE,
        ev_special_attack=ZERO_VALUE,
        special_defense=pokemon.special_defense,
        iv_special_defense=ZERO_VALUE,
        ev_special_defense=ZERO_VALUE,
        pokemon=pokemon,
        formula=formula,
    )


class TestPokemonProgressionBusinessCalculateIvs:
    """Test scope for calculate ivs method"""

    @staticmethod
    def test_calculate_ivs():
        """Should return ivs calculate"""
        business = PokemonProgressionBusiness()
        result = business._calculate_ivs()

        assert MIN_IV_EV <= result.hp <= MAX_IV, 'IV should be between 0 and 31'
        assert MIN_IV_EV <= result.speed <= MAX_IV, 'IV should be between 0 and 31'
        assert MIN_IV_EV <= result.attack <= MAX_IV, 'IV should be between 0 and 31'
        assert MIN_IV_EV <= result.defense <= MAX_IV, 'IV should be between 0 and 31'
        assert MIN_IV_EV <= result.special_attack <= MAX_IV, 'IV should be between 0 and 31'
        assert MIN_IV_EV <= result.special_defense <= MAX_IV, 'IV should be between 0 and 31'


class TestPokemonProgressionBusinessCalculateEvs:
    """Test scope for calculate evs method"""

    @staticmethod
    def test_calculate_evs():
        """Should return iv calculate"""
        business = PokemonProgressionBusiness()
        result = business._calculate_evs()

        assert MIN_IV_EV <= result.hp <= MAX_EV, 'EV should be between 0 and 255'
        assert MIN_IV_EV <= result.speed <= MAX_EV, 'EV should be between 0 and 255'
        assert MIN_IV_EV <= result.attack <= MAX_EV, 'EV should be between 0 and 255'
        assert MIN_IV_EV <= result.defense <= MAX_EV, 'EV should be between 0 and 255'
        assert MIN_IV_EV <= result.special_attack <= MAX_EV, 'EV should be between 0 and 255'
        assert MIN_IV_EV <= result.special_defense <= MAX_EV, 'EV should be between 0 and 255'


class TestPokemonProgressionBusinessCalculateStat:
    """Test scope for calculate stats method"""

    @staticmethod
    def test_calculate_stat():
        """Should return stat calculate"""
        business = PokemonProgressionBusiness()
        result_value = 7
        result = business._calculate_stat(
            level=1,
            iv_stat=27,
            ev_stat=248,
            base_stat=97,
            nature_multiple=1.0,
        )
        assert result == result_value, 'Stat calculation should be correct'


class TestPokemonProgressionBusinessInitializeStats:
    @staticmethod
    def test_initialize_stats_pokemon_none():
        """Should return initialize stats empty"""
        business = PokemonProgressionBusiness()
        result = business.initialize_stats()
        assert isinstance(result, ProgressionResult)
        assert result.hp == 0
        assert result.speed == 0
        assert result.attack == 0
        assert result.defense == 0
        assert result.special_attack == 0
        assert result.special_defense == 0

    @staticmethod
    def test_initialize_stats_pokemon_growth_rate_none(pokemon):
        """Should return initialize stats empty"""
        business = PokemonProgressionBusiness()
        result = business.initialize_stats(pokemon=pokemon)
        assert isinstance(result, ProgressionResult)
        assert result.hp == 0
        assert result.speed == 0
        assert result.attack == 0
        assert result.defense == 0
        assert result.special_attack == 0
        assert result.special_defense == 0

    @staticmethod
    def test_initialize_stats_pokemon_success():
        init_experience = 0
        """Should return initialize stats empty"""
        business = PokemonProgressionBusiness()
        pokemon = PokemonFactory(
            hp=78,
            speed=100,
            attack=84,
            defense=78,
            special_attack=109,
            special_defense=85,
            base_experience=240,
        )
        growth_rate = PokemonGrowthRateFactory()
        pokemon.growth_rate = growth_rate
        result = business.initialize_stats(pokemon=pokemon)

        assert isinstance(result, ProgressionResult)
        assert result.hp != pokemon.hp
        assert result.experience == init_experience
        assert result.max_hp != pokemon.hp
        assert result.speed != pokemon.speed
        assert result.attack != pokemon.attack
        assert result.defense != pokemon.defense
        assert result.special_attack != pokemon.special_attack
        assert result.special_defense != pokemon.special_defense


class TestPokemonProgressionBusinessCalculateHp:
    """Test scope for calculate hp method"""

    @staticmethod
    def test_calculate_hp_returns_expected_value():
        """Should calculate HP based on stats and level"""
        business = PokemonProgressionBusiness()
        result = business._calculate_hp(
            hp=HP_BASE,
            iv_hp=ZERO_VALUE,
            ev_hp=ZERO_VALUE,
            level=LEVEL_START,
        )

        assert result == HP_EXPECTED


class TestPokemonProgressionBusinessBuildBaseStats:
    """Test scope for build base stats method"""

    @staticmethod
    def test_build_base_stats_defaults_none_to_zero():
        """Should set missing base stats to zero"""
        pokemon = PokemonFactory()
        pokemon.hp = None
        pokemon.speed = None
        pokemon.attack = None
        pokemon.defense = None
        pokemon.special_attack = None
        pokemon.special_defense = None

        result = PokemonProgressionBusiness._build_base_stats(pokemon)

        assert result == StatBlock(
            hp=ZERO_VALUE,
            speed=ZERO_VALUE,
            attack=ZERO_VALUE,
            defense=ZERO_VALUE,
            special_attack=ZERO_VALUE,
            special_defense=ZERO_VALUE,
        )


class TestPokemonProgressionBusinessCalculateExperience:
    """Test scope for calculate experience method"""

    @staticmethod
    def test_calculate_experience_scales_with_level():
        """Should scale experience by level multiplier"""
        business = PokemonProgressionBusiness()
        result_low = business._calculate_experience(
            level=LEVEL_START, base_experience=BASE_EXPERIENCE
        )
        result_high = business._calculate_experience(
            level=LEVEL_HIGH, base_experience=BASE_EXPERIENCE
        )

        assert result_low == BASE_EXPERIENCE
        assert result_high == BASE_EXPERIENCE * 2


class TestPokemonProgressionBusinessReturnEmpty:
    """Test scope for empty progression result"""

    @staticmethod
    def test_return_empty_progression_result():
        """Should return a fully zeroed progression result"""
        result = PokemonProgressionBusiness._return_empty_progression_result()

        assert result.formula == 'x'
        assert result.hp == ZERO_VALUE
        assert result.speed == ZERO_VALUE
        assert result.attack == ZERO_VALUE
        assert result.defense == ZERO_VALUE
        assert result.special_attack == ZERO_VALUE
        assert result.special_defense == ZERO_VALUE


class TestPokemonProgressionBusinessLevelFromExperience:
    """Test scope for level from experience method"""

    @staticmethod
    def test_level_from_experience_returns_expected_level():
        """Should return the level matching the experience threshold"""
        result = PokemonProgressionBusiness._level_from_experience(
            experience=BASE_EXPERIENCE,
            current_level=LEVEL_START,
            formula=FORMULA_SIMPLE,
        )

        assert result == LEVEL_AFTER_XP


class TestPokemonProgressionBusinessApplyAttackResult:
    """Test scope for apply attack result method"""

    @staticmethod
    def test_apply_attack_result_not_fainted_updates_defender_only():
        """Should update defender HP without leveling when not fainted"""
        business = PokemonProgressionBusiness()
        attacker_pokemon = PokemonFactory(base_experience=BASE_EXPERIENCE)
        defender_pokemon = PokemonFactory(base_experience=BASE_EXPERIENCE)

        attacker = build_battle_schema(
            level=LEVEL_START,
            hp=ATTACKER_HP,
            pokemon=attacker_pokemon,
            formula=FORMULA_SIMPLE,
        )
        defender = build_battle_schema(
            level=LEVEL_START,
            hp=DEFENDER_HP,
            pokemon=defender_pokemon,
            formula=FORMULA_SIMPLE,
        )
        attack_result = AttackResult(
            damage=ATTACK_DAMAGE,
            remaining_hp=5,
            fainted=False,
            critical=False,
            effectiveness=1.0,
            stab=False,
            missed=False,
        )

        result = business.apply_attack_result(attacker, defender, attack_result)

        assert result.level_up is False
        assert result.attacker_progression.level == LEVEL_START
        assert result.attacker_progression.wins == ZERO_VALUE
        assert result.defender_progression.hp == DEFENDER_HP - ATTACK_DAMAGE

    @staticmethod
    def test_apply_attack_result_fainted_grants_experience_and_level():
        """Should grant experience and level up when defender faints"""
        business = PokemonProgressionBusiness()
        attacker_pokemon = PokemonFactory(base_experience=BASE_EXPERIENCE)
        defender_pokemon = PokemonFactory(base_experience=BASE_EXPERIENCE)

        attacker = build_battle_schema(
            level=LEVEL_START,
            hp=ATTACKER_HP,
            pokemon=attacker_pokemon,
            formula=FORMULA_SIMPLE,
        )
        defender = build_battle_schema(
            level=LEVEL_START,
            hp=ATTACK_DAMAGE,
            pokemon=defender_pokemon,
            formula=FORMULA_SIMPLE,
        )
        attack_result = AttackResult(
            damage=ATTACK_DAMAGE,
            remaining_hp=0,
            fainted=True,
            critical=False,
            effectiveness=1.0,
            stab=False,
            missed=False,
        )

        result = business.apply_attack_result(attacker, defender, attack_result)

        assert result.level_up is True
        assert result.attacker_progression.level == LEVEL_AFTER_XP
        assert result.attacker_progression.wins == 1
        assert result.defender_progression.hp == ZERO_VALUE
