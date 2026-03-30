from app.domain.pokemon.external.business.business import PokemonExternalBusiness
from app.domain.pokemon.external.enums.service_enum import ServiceType
from tests.app.domain.pokemon.external.mocks.business_mock import (
    MOCK_ATTRIBUTES_ATTACK,
    MOCK_ATTRIBUTES_DEFENSE,
    MOCK_ATTRIBUTES_HP,
    MOCK_ATTRIBUTES_SPECIAL_ATTACK,
    MOCK_ATTRIBUTES_SPECIAL_DEFENSE,
    MOCK_ATTRIBUTES_SPEED,
    MOCK_EXTERNAL_API_URL,
)
from tests.app.domain.pokemon.external.mocks.external_mock import (
    MOCK_POKEMON_BASE_EXPERIENCE,
    MOCK_POKEMON_HEIGHT,
    MOCK_POKEMON_WEIGHT,
    MOCK_RESPONSE_BY_NAME,
    MOCK_RESPONSE_BY_NAME_SPRITES,
    MOCK_RESPONSE_BY_NAME_SPRITES_DREAM_WORLD,
    MOCK_RESPONSE_BY_SPECIE,
)


class TestPokemonExternalBusinessEnsureImage:
    @staticmethod
    def test_pokemon_external_business_ensure_image_empty():
        result = PokemonExternalBusiness.ensure_image(None)
        assert not result

    @staticmethod
    def test_pokemon_external_business_ensure_image_success():
        result = PokemonExternalBusiness.ensure_image(MOCK_RESPONSE_BY_NAME_SPRITES)
        assert result == MOCK_RESPONSE_BY_NAME_SPRITES.front_default

    @staticmethod
    def test_pokemon_external_business_ensure_image_dream_world():
        result = PokemonExternalBusiness.ensure_image(
            MOCK_RESPONSE_BY_NAME_SPRITES_DREAM_WORLD
        )
        assert result == MOCK_RESPONSE_BY_NAME_SPRITES.front_default


class TestPokemonExternalBusinessEnsureStatisticsAttributes:
    @staticmethod
    def test_pokemon_external_business_ensure_statistics_attributes_empty():
        result = PokemonExternalBusiness.ensure_statistics_attributes([])
        assert result.hp == 0
        assert result.speed == 0
        assert result.attack == 0
        assert result.defense == 0
        assert result.special_attack == 0
        assert result.special_defense == 0

    @staticmethod
    def test_pokemon_external_business_ensure_statistics_attributes_success():
        result = PokemonExternalBusiness.ensure_statistics_attributes(
            MOCK_RESPONSE_BY_NAME.stats
        )
        assert result.hp == MOCK_ATTRIBUTES_HP
        assert result.speed == MOCK_ATTRIBUTES_SPEED
        assert result.attack == MOCK_ATTRIBUTES_ATTACK
        assert result.defense == MOCK_ATTRIBUTES_DEFENSE
        assert result.special_attack == MOCK_ATTRIBUTES_SPECIAL_ATTACK
        assert result.special_defense == MOCK_ATTRIBUTES_SPECIAL_DEFENSE


class TestPokemonExternalBusinessEnsureAttributes:
    @staticmethod
    def test_pokemon_external_business_ensure_attributes_success():
        pokemon_name_success = MOCK_RESPONSE_BY_NAME
        result = PokemonExternalBusiness.ensure_attributes(pokemon_name_success)
        assert result.hp == MOCK_ATTRIBUTES_HP
        assert result.height == MOCK_POKEMON_HEIGHT
        assert result.weight == MOCK_POKEMON_WEIGHT
        assert result.speed == MOCK_ATTRIBUTES_SPEED
        assert result.attack == MOCK_ATTRIBUTES_ATTACK
        assert result.defense == MOCK_ATTRIBUTES_DEFENSE
        assert result.special_attack == MOCK_ATTRIBUTES_SPECIAL_ATTACK
        assert result.special_defense == MOCK_ATTRIBUTES_SPECIAL_DEFENSE
        assert result.base_experience == MOCK_POKEMON_BASE_EXPERIENCE

    @staticmethod
    def test_pokemon_external_business_ensure_attributes_empty():
        pokemon_name_empty = MOCK_RESPONSE_BY_NAME
        pokemon_name_empty.stats = []
        pokemon_name_empty.height = None
        pokemon_name_empty.weight = None
        pokemon_name_empty.base_experience = None
        result = PokemonExternalBusiness.ensure_attributes(pokemon_name_empty)
        assert result.hp == 0
        assert result.height == 0
        assert result.weight == 0
        assert result.speed == 0
        assert result.attack == 0
        assert result.defense == 0
        assert result.special_attack == 0
        assert result.special_defense == 0
        assert result.base_experience == 0


class TestPokemonExternalBusinessEnsureSpecieAttributes:
    @staticmethod
    def test_pokemon_external_business_ensure_specie_attributes_success():
        result_success_specie = MOCK_RESPONSE_BY_SPECIE
        result = PokemonExternalBusiness.ensure_specie_attributes(result_success_specie)
        assert result.habitat == result_success_specie.habitat.name
        assert result.is_baby == result_success_specie.is_baby
        assert result.shape_name == result_success_specie.shape.name
        assert result.shape_url == result_success_specie.shape.url
        assert result.is_mythical == result_success_specie.is_mythical
        assert result.gender_rate == result_success_specie.gender_rate
        assert result.is_legendary == result_success_specie.is_legendary
        assert result.capture_rate == result_success_specie.capture_rate
        assert result.hatch_counter == result_success_specie.hatch_counter
        assert result.base_happiness == result_success_specie.base_happiness
        assert result.evolution_chain_url == result_success_specie.evolution_chain.url
        assert result.evolves_from_species == result_success_specie.evolves_from_species.name
        assert result.has_gender_differences == result_success_specie.has_gender_differences

    @staticmethod
    def test_pokemon_external_business_ensure_specie_attributes_empty():
        result_empty_specie = MOCK_RESPONSE_BY_SPECIE
        result_empty_specie.habitat = None
        result_empty_specie.shape = None
        result_empty_specie.evolution_chain = None
        result_empty_specie.evolves_from_species = None
        result = PokemonExternalBusiness.ensure_specie_attributes(result_empty_specie)
        assert not result.habitat
        assert result.is_baby == result_empty_specie.is_baby
        assert not result.shape_name
        assert not result.shape_url
        assert result.is_mythical == result_empty_specie.is_mythical
        assert result.gender_rate == result_empty_specie.gender_rate
        assert result.is_legendary == result_empty_specie.is_legendary
        assert result.capture_rate == result_empty_specie.capture_rate
        assert result.hatch_counter == result_empty_specie.hatch_counter
        assert result.base_happiness == result_empty_specie.base_happiness
        assert not result.evolution_chain_url
        assert not result.evolves_from_species
        assert result.has_gender_differences == result_empty_specie.has_gender_differences


class TestPokemonExternalBusinessBuildUrl:
    @staticmethod
    def test_pokemon_external_business_build_url_return_url():
        result_url = f'{MOCK_EXTERNAL_API_URL}/pokemon/1'
        result = PokemonExternalBusiness.build_url(
            base_url=MOCK_EXTERNAL_API_URL,
            url=result_url,
            name=None,
            order=None,
            service_type=None,
        )
        assert result == result_url

    @staticmethod
    def test_pokemon_external_business_build_url_return_none():
        result = PokemonExternalBusiness.build_url(
            base_url=MOCK_EXTERNAL_API_URL,
            url=None,
            name=None,
            order=None,
            service_type=None,
        )
        assert not result

    @staticmethod
    def test_pokemon_external_business_build_url_return_service_type():
        result_url = f'{MOCK_EXTERNAL_API_URL}/type/fire'
        result = PokemonExternalBusiness.build_url(
            base_url=MOCK_EXTERNAL_API_URL,
            url=None,
            name='fire',
            order=None,
            service_type=ServiceType.TYPE,
        )
        assert result == result_url

    @staticmethod
    def test_pokemon_external_business_build_url_return_service_move():
        result_url = f'{MOCK_EXTERNAL_API_URL}/move/1'
        result = PokemonExternalBusiness.build_url(
            base_url=MOCK_EXTERNAL_API_URL,
            url=None,
            name=None,
            order=1,
            service_type=ServiceType.MOVE,
        )
        assert result == result_url

    @staticmethod
    def test_pokemon_external_business_build_url_return_service_specie():
        result_url = f'{MOCK_EXTERNAL_API_URL}/pokemon-species/1'
        result = PokemonExternalBusiness.build_url(
            base_url=MOCK_EXTERNAL_API_URL,
            url=None,
            name=None,
            order=1,
            service_type=ServiceType.SPECIE,
        )
        assert result == result_url

    @staticmethod
    def test_pokemon_external_business_build_url_return_service_pokemon_name():
        result_url = f'{MOCK_EXTERNAL_API_URL}/pokemon/bulbasaur'
        result = PokemonExternalBusiness.build_url(
            base_url=MOCK_EXTERNAL_API_URL,
            url=None,
            name='bulbasaur',
            order=None,
            service_type=ServiceType.POKEMON,
        )
        assert result == result_url

    @staticmethod
    def test_pokemon_external_business_build_url_return_service_evolution():
        result_url = f'{MOCK_EXTERNAL_API_URL}/evolution-chain/1'
        result = PokemonExternalBusiness.build_url(
            base_url=MOCK_EXTERNAL_API_URL,
            url=None,
            name=None,
            order=1,
            service_type=ServiceType.EVOLUTION,
        )
        assert result == result_url

    @staticmethod
    def test_pokemon_external_business_build_url_return_service_growth_rate():
        result_url = f'{MOCK_EXTERNAL_API_URL}/growth-rate/1'
        result = PokemonExternalBusiness.build_url(
            base_url=MOCK_EXTERNAL_API_URL,
            url=None,
            name=None,
            order=1,
            service_type=ServiceType.GROWTH_RATE,
        )
        assert result == result_url
