from app.domain.progression.business import PokemonProgressionBusiness
from app.domain.progression.schema import ProgressionResult
from tests.factories.growth_rate import PokemonGrowthRateFactory
from tests.factories.pokemon import PokemonFactory

MIN_IV_EV = 0
MAX_IV = 31
MAX_EV = 255


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
