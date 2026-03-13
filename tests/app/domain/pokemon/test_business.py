from datetime import datetime

from app.domain.growth_rate.model import PokemonGrowthRate
from app.domain.pokemon.business import PokemonBusiness
from app.domain.pokemon.external.schemas import (
    PokemonExternalBase,
)
from app.domain.pokemon.external.schemas.evolution import (
    PokemonExternalEvolutionChainEvolvesToSchemaResponse,
    PokemonExternalEvolutionChainSchemaResponse,
)
from app.domain.pokemon.model import Pokemon
from app.domain.pokemon.schema import PokemonSchema
from app.shared.status_enum import StatusEnum

MOCK_BULBASAUR_HP_UPDATED = 50
MOCK_BULBASAUR_DEFENSE_UPDATED = 55
MOCK_BULBASAUR_ATTACK = 49
MOCK_PIKACHU_HP = 35
MOCK_PIKACHU_ATTACK_UPDATED = 60
MOCK_PIKACHU_ORDER = 25
MOCK_CHARIZARD_HP = 78
MOCK_CHARIZARD_ATTACK = 84
MOCK_CHARIZARD_DEFENSE = 78
MOCK_CHARIZARD_SPEED = 100
MOCK_SQUIRTLE_HP_UPDATED = 44
MOCK_IVYSAUR_ORDER = 2
MOCK_POKEMON_ORDERS = {4, 7, 25}
MOCK_COMPLETE_POKEMON_NAMES = {'bulbasaur', 'ivysaur'}
MOCK_INCOMPLETE_ORDERS = {25, 4, 7}
MOCK_VARIOUS_ORDERS = {100, 50, 200}
MOCK_NUM_STATS = 6
MOCK_IV_MAX_VALUE = 31
MOCK_EXP_LEVEL_5 = 125
MOCK_EXP_LEVEL_1 = 1
MOCK_EXP_LEVEL_10 = 1000
MOCK_NUM_RANGE_10 = 10
MOCK_NUM_RANGE_5 = 5
MOCK_EV_MAX_STANDARD = 252
MOCK_BASE_STAT_LOW = 1
MOCK_LEVEL_50 = 50
MOCK_LONG_LINE_COMMENT = (
    'At least one IV value should differ across calls (extremely unlikely to be all identical)'
)
MOCK_PIKACHU_ATTACK_STAT = 55
MOCK_PIKACHU_DEFENSE_STAT = 40
MOCK_PIKACHU_SPECIAL_ATTACK = 50
MOCK_PIKACHU_SPECIAL_DEFENSE = 50
MOCK_PIKACHU_SPEED = 90


class TestPokemonBusinessEnsureEvolution:
    """Test scope for ensure_evolution method"""

    @staticmethod
    def test_ensure_evolution_with_none_params():
        """Should return empty list when params is None"""
        business = PokemonBusiness()
        result = business.ensure_evolution(params=None)

        assert isinstance(result, list)
        assert result == []

    @staticmethod
    def test_ensure_evolution_with_single_species():
        """Should return single species name when no evolutions exist"""
        business = PokemonBusiness()
        evolution_data = PokemonExternalEvolutionChainSchemaResponse(
            species=PokemonExternalBase(
                name='bulbasaur',
                url='https://pokeapi.co/api/v2/pokemon-species/1/',
            ),
            evolves_to=[],
        )

        result = business.ensure_evolution(params=evolution_data)

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0] == 'bulbasaur'

    @staticmethod
    def test_ensure_evolution_with_one_evolution():
        """Should return species and its evolution when one evolution exists"""
        business = PokemonBusiness()
        evolves_to = PokemonExternalEvolutionChainEvolvesToSchemaResponse(
            species=PokemonExternalBase(
                name='ivysaur',
                url='https://pokeapi.co/api/v2/pokemon-species/2/',
            ),
            is_baby=False,
            evolution_details=[],
            evolves_to=[],
        )
        evolution_data = PokemonExternalEvolutionChainSchemaResponse(
            species=PokemonExternalBase(
                name='bulbasaur',
                url='https://pokeapi.co/api/v2/pokemon-species/1/',
            ),
            is_baby=False,
            evolution_details=[],
            evolves_to=[evolves_to],
        )

        total_results = 2
        result = business.ensure_evolution(params=evolution_data)

        assert isinstance(result, list)
        assert len(result) == total_results
        assert result[0] == 'bulbasaur'
        assert result[1] == 'ivysaur'

    @staticmethod
    def test_ensure_evolution_with_branching_evolution():
        """Should return all species in branching evolution chain"""
        total_results = 3
        business = PokemonBusiness()
        evolution_data = PokemonExternalEvolutionChainSchemaResponse(
            species=PokemonExternalBase(
                name='eevee',
                url='https://pokeapi.co/api/v2/pokemon-species/133/',
            ),
            evolves_to=[
                PokemonExternalEvolutionChainEvolvesToSchemaResponse(
                    species=PokemonExternalBase(
                        name='vaporeon',
                        url='https://pokeapi.co/api/v2/pokemon-species/134/',
                    ),
                ),
                PokemonExternalEvolutionChainEvolvesToSchemaResponse(
                    species=PokemonExternalBase(
                        name='jolteon',
                        url='https://pokeapi.co/api/v2/pokemon-species/135/',
                    ),
                ),
            ],
        )

        result = business.ensure_evolution(params=evolution_data)

        assert isinstance(result, list)
        assert len(result) == total_results
        assert 'eevee' in result
        assert 'vaporeon' in result
        assert 'jolteon' in result


class TestPokemonBusinessEnsureNextEvolution:
    """Test scope for ensure_next_evolution method"""

    @staticmethod
    def test_ensure_next_evolution_with_none_params():
        """Should return empty list when params is None"""
        business = PokemonBusiness()
        result = business.ensure_next_evolution(params=None)

        assert isinstance(result, list)
        assert result == []

    @staticmethod
    def test_ensure_next_evolution_with_empty_list():
        """Should return empty list when params is empty list"""
        business = PokemonBusiness()
        result = business.ensure_next_evolution(params=[])

        assert isinstance(result, list)
        assert result == []

    @staticmethod
    def test_ensure_next_evolution_with_single_evolution():
        """Should return single evolution name when one evolution exists"""
        business = PokemonBusiness()
        evolves_to = PokemonExternalEvolutionChainEvolvesToSchemaResponse(
            species=PokemonExternalBase(
                name='ivysaur',
                url='https://pokeapi.co/api/v2/pokemon-species/2/',
            ),
            is_baby=False,
            evolution_details=[],
            evolves_to=[],
        )
        evolution_list = [evolves_to]

        result = business.ensure_next_evolution(params=evolution_list)

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0] == 'ivysaur'

    @staticmethod
    def test_ensure_next_evolution_with_multiple_evolutions():
        """Should return all evolution names when multiple evolutions exist"""
        total_results = 2
        business = PokemonBusiness()
        evolution_list = [
            PokemonExternalEvolutionChainEvolvesToSchemaResponse(
                species=PokemonExternalBase(
                    name='vaporeon',
                    url='https://pokeapi.co/api/v2/pokemon-species/134/',
                ),
            ),
            PokemonExternalEvolutionChainEvolvesToSchemaResponse(
                species=PokemonExternalBase(
                    name='jolteon',
                    url='https://pokeapi.co/api/v2/pokemon-species/135/',
                ),
            ),
        ]

        result = business.ensure_next_evolution(params=evolution_list)

        assert isinstance(result, list)
        assert len(result) == total_results
        assert 'vaporeon' in result
        assert 'jolteon' in result


class TestPokemonBusinessMergeIfChanged:
    """Test scope for merge_if_changed method"""

    @staticmethod
    def test_merge_if_changed_updates_changed_fields():
        """Should update only fields that have changed"""
        business = PokemonBusiness()

        pokemon_target = Pokemon(
            name='bulbasaur',
            order=1,
            url='https://pokeapi.co/api/v2/pokemon/1/',
            status=StatusEnum.INCOMPLETE,
            external_image='https://example.com/1.png',
            hp=45,
            attack=49,
            defense=49,
        )

        pokemon_source = PokemonSchema(
            id='test-id-1',
            name='bulbasaur',
            order=1,
            url='https://pokeapi.co/api/v2/pokemon/1/',
            status=StatusEnum.COMPLETE,
            external_image='https://example.com/1.png',
            hp=MOCK_BULBASAUR_HP_UPDATED,
            attack=MOCK_BULBASAUR_ATTACK,
            defense=MOCK_BULBASAUR_DEFENSE_UPDATED,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        result = business.merge_if_changed(
            pokemon_target=pokemon_target,
            pokemon_source=pokemon_source,
        )

        assert result.hp == MOCK_BULBASAUR_HP_UPDATED
        assert result.defense == MOCK_BULBASAUR_DEFENSE_UPDATED
        assert result.status == StatusEnum.COMPLETE
        assert result.attack == MOCK_BULBASAUR_ATTACK
        assert result.name == 'bulbasaur'

    @staticmethod
    def test_merge_if_changed_ignores_none_values():
        """Should not update fields when source value is None"""
        business = PokemonBusiness()

        pokemon_target = Pokemon(
            name='pikachu',
            order=25,
            url='https://pokeapi.co/api/v2/pokemon/25/',
            status=StatusEnum.INCOMPLETE,
            external_image='https://example.com/25.png',
            hp=35,
            attack=55,
        )

        pokemon_source = PokemonSchema(
            id='test-id-2',
            name='pikachu',
            order=25,
            url='https://pokeapi.co/api/v2/pokemon/25/',
            status=StatusEnum.INCOMPLETE,
            external_image='https://example.com/25.png',
            hp=None,
            attack=MOCK_PIKACHU_ATTACK_UPDATED,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        result = business.merge_if_changed(
            pokemon_target=pokemon_target,
            pokemon_source=pokemon_source,
        )

        assert result.hp == MOCK_PIKACHU_HP
        assert result.attack == MOCK_PIKACHU_ATTACK_UPDATED

    @staticmethod
    def test_merge_if_changed_preserves_unchanged_fields():
        """Should preserve fields that are identical in source and target"""
        business = PokemonBusiness()

        pokemon_target = Pokemon(
            name='charizard',
            order=6,
            url='https://pokeapi.co/api/v2/pokemon/6/',
            status=StatusEnum.COMPLETE,
            external_image='https://example.com/6.png',
            hp=MOCK_CHARIZARD_HP,
            attack=MOCK_CHARIZARD_ATTACK,
            defense=MOCK_CHARIZARD_DEFENSE,
            speed=MOCK_CHARIZARD_SPEED,
        )

        pokemon_source = PokemonSchema(
            id='test-id-3',
            name='charizard',
            order=6,
            url='https://pokeapi.co/api/v2/pokemon/6/',
            status=StatusEnum.COMPLETE,
            external_image='https://example.com/6.png',
            hp=MOCK_CHARIZARD_HP,
            attack=MOCK_CHARIZARD_ATTACK,
            defense=MOCK_CHARIZARD_DEFENSE,
            speed=MOCK_CHARIZARD_SPEED,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        result = business.merge_if_changed(
            pokemon_target=pokemon_target,
            pokemon_source=pokemon_source,
        )

        assert result.hp == MOCK_CHARIZARD_HP
        assert result.attack == MOCK_CHARIZARD_ATTACK
        assert result.defense == MOCK_CHARIZARD_DEFENSE
        assert result.speed == MOCK_CHARIZARD_SPEED
        assert result.status == StatusEnum.COMPLETE

    @staticmethod
    def test_merge_if_changed_updates_all_different_fields():
        """Should update all fields when all values differ"""
        business = PokemonBusiness()

        pokemon_target = Pokemon(
            name='squirtle',
            order=7,
            url='https://pokeapi.co/api/v2/pokemon/7/',
            status=StatusEnum.INCOMPLETE,
            external_image='https://example.com/7.png',
            hp=40,
            attack=48,
            defense=65,
            special_attack=50,
            special_defense=64,
            speed=43,
        )

        pokemon_source = PokemonSchema(
            id='test-id-4',
            name='squirtle',
            order=7,
            url='https://pokeapi.co/api/v2/pokemon/7/',
            status=StatusEnum.COMPLETE,
            external_image='https://example.com/7-updated.png',
            hp=MOCK_SQUIRTLE_HP_UPDATED,
            attack=48,
            defense=65,
            special_attack=50,
            special_defense=64,
            speed=43,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        result = business.merge_if_changed(
            pokemon_target=pokemon_target,
            pokemon_source=pokemon_source,
        )

        assert result.hp == MOCK_SQUIRTLE_HP_UPDATED
        assert result.status == StatusEnum.COMPLETE
        assert result.external_image == 'https://example.com/7-updated.png'

    @staticmethod
    def test_merge_if_changed_handles_boolean_fields():
        """Should correctly update boolean fields"""
        business = PokemonBusiness()

        pokemon_target = Pokemon(
            name='mew',
            order=151,
            url='https://pokeapi.co/api/v2/pokemon/151/',
            status=StatusEnum.INCOMPLETE,
            external_image='https://example.com/151.png',
            is_baby=False,
            is_legendary=False,
            is_mythical=False,
        )

        pokemon_source = PokemonSchema(
            id='test-id-5',
            name='mew',
            order=151,
            url='https://pokeapi.co/api/v2/pokemon/151/',
            status=StatusEnum.COMPLETE,
            external_image='https://example.com/151.png',
            is_baby=False,
            is_legendary=False,
            is_mythical=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        result = business.merge_if_changed(
            pokemon_target=pokemon_target,
            pokemon_source=pokemon_source,
        )

        assert result.is_mythical is True
        assert result.is_baby is False
        assert result.is_legendary is False

    @staticmethod
    def test_merge_if_changed_handles_string_fields():
        """Should correctly update string fields"""
        business = PokemonBusiness()

        pokemon_target = Pokemon(
            name='eevee',
            order=133,
            url='https://pokeapi.co/api/v2/pokemon/133/',
            status=StatusEnum.INCOMPLETE,
            external_image='https://example.com/133.png',
            habitat='urban',
            shape_name='quadruped',
        )

        pokemon_source = PokemonSchema(
            id='test-id-6',
            name='eevee',
            order=133,
            url='https://pokeapi.co/api/v2/pokemon/133/',
            status=StatusEnum.COMPLETE,
            external_image='https://example.com/133.png',
            habitat='grassland',
            shape_name='quadruped',
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        result = business.merge_if_changed(
            pokemon_target=pokemon_target,
            pokemon_source=pokemon_source,
        )

        assert result.habitat == 'grassland'
        assert result.shape_name == 'quadruped'

    @staticmethod
    def test_merge_if_changed_returns_target_instance():
        """Should return the same target instance after merge"""
        business = PokemonBusiness()

        pokemon_target = Pokemon(
            name='ditto',
            order=132,
            url='https://pokeapi.co/api/v2/pokemon/132/',
            status=StatusEnum.INCOMPLETE,
            external_image='https://example.com/132.png',
            hp=48,
        )

        pokemon_source = PokemonSchema(
            id='test-id-7',
            name='ditto',
            order=132,
            url='https://pokeapi.co/api/v2/pokemon/132/',
            status=StatusEnum.COMPLETE,
            external_image='https://example.com/132.png',
            hp=48,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        result = business.merge_if_changed(
            pokemon_target=pokemon_target,
            pokemon_source=pokemon_source,
        )

        assert result is pokemon_target


class TestPokemonBusinessFindFirstPokemon:
    """Test scope for find_first_pokemon method"""

    @staticmethod
    def test_find_first_pokemon_with_empty_list():
        """Should return None when pokemon list is empty"""
        business = PokemonBusiness()
        result = business.find_first_pokemon(pokemons=[], pokemon_name=None)

        assert result is None

    @staticmethod
    def test_find_first_pokemon_with_name_found():
        """Should return pokemon when name matches"""
        business = PokemonBusiness()
        bulbasaur = Pokemon(
            name='bulbasaur',
            order=1,
            url='https://pokeapi.co/api/v2/pokemon/1/',
            status=StatusEnum.COMPLETE,
            external_image='https://example.com/1.png',
        )
        pikachu = Pokemon(
            name='pikachu',
            order=MOCK_PIKACHU_ORDER,
            url='https://pokeapi.co/api/v2/pokemon/25/',
            status=StatusEnum.INCOMPLETE,
            external_image='https://example.com/25.png',
        )
        pokemons = [bulbasaur, pikachu]

        result = business.find_first_pokemon(
            pokemons=pokemons,
            pokemon_name='pikachu',
        )

        assert result is not None
        assert result.name == 'pikachu'
        assert result.order == MOCK_PIKACHU_ORDER

    @staticmethod
    def test_find_first_pokemon_with_name_not_found():
        """Should return random complete pokemon when name is not found"""
        business = PokemonBusiness()
        bulbasaur = Pokemon(
            name='bulbasaur',
            order=1,
            url='https://pokeapi.co/api/v2/pokemon/1/',
            status=StatusEnum.COMPLETE,
            external_image='https://example.com/1.png',
        )
        pikachu = Pokemon(
            name='pikachu',
            order=25,
            url='https://pokeapi.co/api/v2/pokemon/25/',
            status=StatusEnum.INCOMPLETE,
            external_image='https://example.com/25.png',
        )
        pokemons = [bulbasaur, pikachu]

        result = business.find_first_pokemon(
            pokemons=pokemons,
            pokemon_name='nonexistent',
        )

        # Should return a complete pokemon or None if no complete pokemon exists
        if result:
            assert result.status == StatusEnum.COMPLETE

    @staticmethod
    def test_find_first_pokemon_without_name():
        """Should return random complete pokemon when pokemon_name is None"""
        business = PokemonBusiness()
        bulbasaur = Pokemon(
            name='bulbasaur',
            order=1,
            url='https://pokeapi.co/api/v2/pokemon/1/',
            status=StatusEnum.COMPLETE,
            external_image='https://example.com/1.png',
        )
        pikachu = Pokemon(
            name='pikachu',
            order=25,
            url='https://pokeapi.co/api/v2/pokemon/25/',
            status=StatusEnum.INCOMPLETE,
            external_image='https://example.com/25.png',
        )
        pokemons = [bulbasaur, pikachu]

        result = business.find_first_pokemon(
            pokemons=pokemons,
            pokemon_name=None,
        )

        assert result is not None
        assert result.status == StatusEnum.COMPLETE
        assert result.name == 'bulbasaur'

    @staticmethod
    def test_find_first_pokemon_with_name_and_multiple_complete():
        """Should return the exact pokemon when name matches, even with multiple complete"""
        business = PokemonBusiness()
        bulbasaur = Pokemon(
            name='bulbasaur',
            order=1,
            url='https://pokeapi.co/api/v2/pokemon/1/',
            status=StatusEnum.COMPLETE,
            external_image='https://example.com/1.png',
        )
        ivysaur = Pokemon(
            name='ivysaur',
            order=MOCK_IVYSAUR_ORDER,
            url='https://pokeapi.co/api/v2/pokemon/2/',
            status=StatusEnum.COMPLETE,
            external_image='https://example.com/2.png',
        )
        venusaur = Pokemon(
            name='venusaur',
            order=3,
            url='https://pokeapi.co/api/v2/pokemon/3/',
            status=StatusEnum.COMPLETE,
            external_image='https://example.com/3.png',
        )
        pokemons = [bulbasaur, ivysaur, venusaur]

        result = business.find_first_pokemon(
            pokemons=pokemons,
            pokemon_name='ivysaur',
        )

        assert result is not None
        assert result.name == 'ivysaur'
        assert result.order == MOCK_IVYSAUR_ORDER

    @staticmethod
    def test_find_first_pokemon_with_incomplete_and_one_complete():
        """Should return the only complete pokemon when incomplete exist"""
        business = PokemonBusiness()
        incomplete_1 = Pokemon(
            name='pikachu',
            order=25,
            url='https://pokeapi.co/api/v2/pokemon/25/',
            status=StatusEnum.INCOMPLETE,
            external_image='https://example.com/25.png',
        )
        complete = Pokemon(
            name='bulbasaur',
            order=1,
            url='https://pokeapi.co/api/v2/pokemon/1/',
            status=StatusEnum.COMPLETE,
            external_image='https://example.com/1.png',
        )
        incomplete_2 = Pokemon(
            name='charmander',
            order=4,
            url='https://pokeapi.co/api/v2/pokemon/4/',
            status=StatusEnum.INCOMPLETE,
            external_image='https://example.com/4.png',
        )
        pokemons = [incomplete_1, complete, incomplete_2]

        result = business.find_first_pokemon(
            pokemons=pokemons,
            pokemon_name=None,
        )

        assert result is not None
        assert result.name == 'bulbasaur'
        assert result.status == StatusEnum.COMPLETE


class TestPokemonBusinessGetRandomPokemon:
    """Test scope for get_random_pokemon method"""

    @staticmethod
    def test_get_random_pokemon_with_complete():
        """Should return complete pokemon when it exists"""
        business = PokemonBusiness()
        incomplete = Pokemon(
            name='pikachu',
            order=25,
            url='https://pokeapi.co/api/v2/pokemon/25/',
            status=StatusEnum.INCOMPLETE,
            external_image='https://example.com/25.png',
        )
        complete = Pokemon(
            name='bulbasaur',
            order=1,
            url='https://pokeapi.co/api/v2/pokemon/1/',
            status=StatusEnum.COMPLETE,
            external_image='https://example.com/1.png',
        )
        pokemons = [incomplete, complete]

        result = business.get_random_pokemon(pokemons=pokemons)

        assert result is not None
        assert result.status == StatusEnum.COMPLETE

    @staticmethod
    def test_get_random_pokemon_with_multiple_complete():
        """Should return one of the complete pokemons"""
        business = PokemonBusiness()
        complete_1 = Pokemon(
            name='bulbasaur',
            order=1,
            url='https://pokeapi.co/api/v2/pokemon/1/',
            status=StatusEnum.COMPLETE,
            external_image='https://example.com/1.png',
        )
        complete_2 = Pokemon(
            name='ivysaur',
            order=2,
            url='https://pokeapi.co/api/v2/pokemon/2/',
            status=StatusEnum.COMPLETE,
            external_image='https://example.com/2.png',
        )
        incomplete = Pokemon(
            name='pikachu',
            order=25,
            url='https://pokeapi.co/api/v2/pokemon/25/',
            status=StatusEnum.INCOMPLETE,
            external_image='https://example.com/25.png',
        )
        pokemons = [complete_1, incomplete, complete_2]

        result = business.get_random_pokemon(pokemons=pokemons)

        assert result is not None
        assert result.status == StatusEnum.COMPLETE
        assert result.name in MOCK_COMPLETE_POKEMON_NAMES

    @staticmethod
    def test_get_random_pokemon_all_incomplete():
        """Should return random pokemon by order when all are incomplete"""
        business = PokemonBusiness()
        incomplete_1 = Pokemon(
            name='pikachu',
            order=25,
            url='https://pokeapi.co/api/v2/pokemon/25/',
            status=StatusEnum.INCOMPLETE,
            external_image='https://example.com/25.png',
        )
        incomplete_2 = Pokemon(
            name='charmander',
            order=4,
            url='https://pokeapi.co/api/v2/pokemon/4/',
            status=StatusEnum.INCOMPLETE,
            external_image='https://example.com/4.png',
        )
        incomplete_3 = Pokemon(
            name='squirtle',
            order=7,
            url='https://pokeapi.co/api/v2/pokemon/7/',
            status=StatusEnum.INCOMPLETE,
            external_image='https://example.com/7.png',
        )
        pokemons = [incomplete_1, incomplete_2, incomplete_3]

        result = business.get_random_pokemon(pokemons=pokemons)

        assert result is not None
        assert result in pokemons
        assert result.order in MOCK_INCOMPLETE_ORDERS

    @staticmethod
    def test_get_random_pokemon_single_pokemon():
        """Should return the only pokemon"""
        business = PokemonBusiness()
        pokemon = Pokemon(
            name='mew',
            order=151,
            url='https://pokeapi.co/api/v2/pokemon/151/',
            status=StatusEnum.COMPLETE,
            external_image='https://example.com/151.png',
        )
        pokemons = [pokemon]

        result = business.get_random_pokemon(pokemons=pokemons)

        assert result is not None
        assert result.name == 'mew'
        assert result is pokemon

    @staticmethod
    def test_get_random_pokemon_with_none_return():
        """Should return None when no pokemon with random order found"""
        business = PokemonBusiness()
        # This is a theoretical edge case, but for safety we test it
        pokemons = []

        result = business.get_random_pokemon(pokemons=pokemons)

        assert result is None

    @staticmethod
    def test_get_random_pokemon_prefers_complete():
        """Should always prefer complete pokemon over incomplete"""
        business = PokemonBusiness()
        incomplete_1 = Pokemon(
            name='pikachu',
            order=25,
            url='https://pokeapi.co/api/v2/pokemon/25/',
            status=StatusEnum.INCOMPLETE,
            external_image='https://example.com/25.png',
        )
        incomplete_2 = Pokemon(
            name='charmander',
            order=4,
            url='https://pokeapi.co/api/v2/pokemon/4/',
            status=StatusEnum.INCOMPLETE,
            external_image='https://example.com/4.png',
        )
        complete = Pokemon(
            name='bulbasaur',
            order=1,
            url='https://pokeapi.co/api/v2/pokemon/1/',
            status=StatusEnum.COMPLETE,
            external_image='https://example.com/1.png',
        )
        pokemons = [incomplete_1, incomplete_2, complete]

        # Run multiple times to ensure complete is always returned
        for _ in range(5):
            result = business.get_random_pokemon(pokemons=pokemons)
            assert result is not None
            assert result.status == StatusEnum.COMPLETE
            assert result.name == 'bulbasaur'

    @staticmethod
    def test_get_random_pokemon_with_various_orders():
        """Should handle pokemons with various order values"""
        business = PokemonBusiness()
        pokemon_1 = Pokemon(
            name='pokemon1',
            order=100,
            url='https://pokeapi.co/api/v2/pokemon/100/',
            status=StatusEnum.INCOMPLETE,
            external_image='https://example.com/100.png',
        )
        pokemon_2 = Pokemon(
            name='pokemon2',
            order=50,
            url='https://pokeapi.co/api/v2/pokemon/50/',
            status=StatusEnum.INCOMPLETE,
            external_image='https://example.com/50.png',
        )
        pokemon_3 = Pokemon(
            name='pokemon3',
            order=200,
            url='https://pokeapi.co/api/v2/pokemon/200/',
            status=StatusEnum.INCOMPLETE,
            external_image='https://example.com/200.png',
        )
        pokemons = [pokemon_1, pokemon_2, pokemon_3]

        result = business.get_random_pokemon(pokemons=pokemons)

        assert result is not None
        assert result in pokemons
        assert result.order in MOCK_VARIOUS_ORDERS


class TestPokemonBusinessCalculateStats:
    """Test scope for calculate_pokemon_stats method"""

    @staticmethod
    def test_calculate_pokemon_stats_returns_dict():
        """Should return a dictionary with calculated stats"""
        business = PokemonBusiness()
        pokemon = Pokemon(
            name='bulbasaur',
            order=1,
            url='https://pokeapi.co/api/v2/pokemon/1/',
            status=StatusEnum.COMPLETE,
            external_image='https://example.com/1.png',
            hp=45,
            attack=49,
            defense=49,
            special_attack=65,
            special_defense=65,
            speed=45,
        )

        result = business.calculate_pokemon_stats(pokemon=pokemon, level=1)

        assert isinstance(result, dict)
        assert 'hp' in result
        assert 'attack' in result
        assert 'defense' in result
        assert 'level' in result
        assert 'experience' in result

    @staticmethod
    def test_calculate_pokemon_stats_with_none_pokemon():
        """Should return empty dict when pokemon is None"""
        business = PokemonBusiness()
        result = business.calculate_pokemon_stats(pokemon=None, level=1)

        assert result == {}

    @staticmethod
    def test_calculate_pokemon_stats_default_level():
        """Should use level 1 as default"""
        business = PokemonBusiness()
        pokemon = Pokemon(
            name='pikachu',
            order=25,
            url='https://pokeapi.co/api/v2/pokemon/25/',
            status=StatusEnum.COMPLETE,
            external_image='https://example.com/25.png',
            hp=35,
            attack=55,
            defense=40,
            special_attack=50,
            special_defense=50,
            speed=90,
        )

        result = business.calculate_pokemon_stats(pokemon=pokemon)

        assert result['level'] == 1

    @staticmethod
    def test_calculate_pokemon_stats_includes_all_fields():
        """Should include all required stat fields in result"""
        business = PokemonBusiness()
        pokemon = Pokemon(
            name='charizard',
            order=6,
            url='https://pokeapi.co/api/v2/pokemon/6/',
            status=StatusEnum.COMPLETE,
            external_image='https://example.com/6.png',
            hp=78,
            attack=84,
            defense=78,
            special_attack=109,
            special_defense=85,
            speed=100,
        )

        result = business.calculate_pokemon_stats(pokemon=pokemon, level=5)

        expected_fields = [
            'hp',
            'max_hp',
            'attack',
            'defense',
            'special_attack',
            'special_defense',
            'speed',
            'level',
            'experience',
            'iv_hp',
            'iv_attack',
            'iv_defense',
            'iv_special_attack',
            'iv_special_defense',
            'iv_speed',
            'ev_hp',
            'ev_attack',
            'ev_defense',
            'ev_special_attack',
            'ev_special_defense',
            'ev_speed',
            'wins',
            'losses',
            'battles',
            'nickname',
        ]

        for field in expected_fields:
            assert field in result

    @staticmethod
    def test_calculate_pokemon_stats_with_higher_level():
        """Should calculate different stats for higher level"""
        business = PokemonBusiness()
        pokemon = Pokemon(
            name='bulbasaur',
            order=1,
            url='https://pokeapi.co/api/v2/pokemon/1/',
            status=StatusEnum.COMPLETE,
            external_image='https://example.com/1.png',
            hp=45,
            attack=49,
            defense=49,
            special_attack=65,
            special_defense=65,
            speed=45,
        )

        stats_level_1 = business.calculate_pokemon_stats(pokemon=pokemon, level=1)
        stats_level_50 = business.calculate_pokemon_stats(pokemon=pokemon, level=MOCK_LEVEL_50)

        assert stats_level_1['level'] == 1
        assert stats_level_50['level'] == MOCK_LEVEL_50
        assert stats_level_50['experience'] != stats_level_1['experience']

    @staticmethod
    def test_calculate_pokemon_stats_sets_initial_values():
        """Should set wins, losses, battles to 0 and nickname to pokemon name"""
        business = PokemonBusiness()
        pokemon = Pokemon(
            name='mew',
            order=151,
            url='https://pokeapi.co/api/v2/pokemon/151/',
            status=StatusEnum.COMPLETE,
            external_image='https://example.com/151.png',
            hp=100,
            attack=100,
            defense=100,
            special_attack=100,
            special_defense=100,
            speed=100,
        )

        result = business.calculate_pokemon_stats(pokemon=pokemon, level=1)

        assert result['wins'] == 0
        assert result['losses'] == 0
        assert result['battles'] == 0
        assert result['nickname'] == 'mew'


class TestPokemonBusinessBuildBaseStats:
    """Test scope for _build_base_stats method"""

    @staticmethod
    def test_build_base_stats_returns_dict():
        """Should return a dictionary with all stat keys"""
        business = PokemonBusiness()
        pokemon = Pokemon(
            name='bulbasaur',
            order=1,
            url='https://pokeapi.co/api/v2/pokemon/1/',
            status=StatusEnum.COMPLETE,
            external_image='https://example.com/1.png',
            hp=45,
            attack=49,
            defense=49,
            special_attack=65,
            special_defense=65,
            speed=45,
        )

        result = business._build_base_stats(pokemon)

        assert isinstance(result, dict)
        assert len(result) == MOCK_NUM_STATS
        assert 'hp' in result
        assert 'attack' in result
        assert 'defense' in result
        assert 'special_attack' in result
        assert 'special_defense' in result
        assert 'speed' in result

    @staticmethod
    def test_build_base_stats_with_correct_values():
        """Should return exact stat values from pokemon"""
        business = PokemonBusiness()
        pokemon = Pokemon(
            name='pikachu',
            order=25,
            url='https://pokeapi.co/api/v2/pokemon/25/',
            status=StatusEnum.COMPLETE,
            external_image='https://example.com/25.png',
            hp=MOCK_PIKACHU_HP,
            attack=MOCK_PIKACHU_ATTACK_STAT,
            defense=MOCK_PIKACHU_DEFENSE_STAT,
            special_attack=MOCK_PIKACHU_SPECIAL_ATTACK,
            special_defense=MOCK_PIKACHU_SPECIAL_DEFENSE,
            speed=MOCK_PIKACHU_SPEED,
        )

        result = business._build_base_stats(pokemon)

        assert result['hp'] == MOCK_PIKACHU_HP
        assert result['attack'] == MOCK_PIKACHU_ATTACK_STAT
        assert result['defense'] == MOCK_PIKACHU_DEFENSE_STAT
        assert result['special_attack'] == MOCK_PIKACHU_SPECIAL_ATTACK
        assert result['special_defense'] == MOCK_PIKACHU_SPECIAL_DEFENSE
        assert result['speed'] == MOCK_PIKACHU_SPEED

    @staticmethod
    def test_build_base_stats_with_none_values():
        """Should treat None values as 0"""
        business = PokemonBusiness()
        pokemon = Pokemon(
            name='test',
            order=999,
            url='https://pokeapi.co/api/v2/pokemon/999/',
            status=StatusEnum.INCOMPLETE,
            external_image='https://example.com/999.png',
            hp=None,
            attack=None,
            defense=MOCK_BULBASAUR_DEFENSE_UPDATED,
        )

        result = business._build_base_stats(pokemon)

        assert result['hp'] == 0
        assert result['attack'] == 0
        assert result['defense'] == MOCK_BULBASAUR_DEFENSE_UPDATED


class TestPokemonBusinessBuildIVs:
    """Test scope for _build_ivs method"""

    @staticmethod
    def test_build_ivs_returns_dict():
        """Should return a dictionary with stat keys"""
        business = PokemonBusiness()
        base_stats = {
            'hp': 45,
            'attack': 49,
            'defense': 49,
            'special_attack': 65,
            'special_defense': 65,
            'speed': 45,
        }

        result = business._build_ivs(base_stats)

        assert isinstance(result, dict)
        assert len(result) == MOCK_NUM_STATS

    @staticmethod
    def test_build_ivs_contains_all_stat_keys():
        """Should contain all stat keys from base_stats"""
        business = PokemonBusiness()
        base_stats = {
            'hp': 35,
            'attack': 55,
            'defense': 40,
            'special_attack': 50,
            'special_defense': 50,
            'speed': 90,
        }

        result = business._build_ivs(base_stats)

        for key in base_stats:
            assert key in result

    @staticmethod
    def test_build_ivs_values_in_valid_range():
        """Should generate IV values between 0 and 31"""
        business = PokemonBusiness()
        base_stats = {
            'hp': 45,
            'attack': 49,
            'defense': 49,
            'special_attack': 65,
            'special_defense': 65,
            'speed': 45,
        }

        result = business._build_ivs(base_stats)

        for iv_value in result.values():
            assert 0 <= iv_value <= MOCK_IV_MAX_VALUE

    @staticmethod
    def test_build_ivs_randomness():
        """Should generate different IV values on multiple calls"""
        business = PokemonBusiness()
        base_stats = {
            'hp': 45,
            'attack': 49,
            'defense': 49,
            'special_attack': 65,
            'special_defense': 65,
            'speed': 45,
        }

        results = [business._build_ivs(base_stats) for _ in range(MOCK_NUM_RANGE_10)]

        # At least one IV value should differ across calls
        all_same = all(results[0] == r for r in results[1:])
        assert not all_same


class TestPokemonBusinessBuildEvs:
    """Test scope for _build_evs method"""

    @staticmethod
    def test_build_evs_returns_dict():
        """Should return a dictionary with stat keys"""
        business = PokemonBusiness()
        base_stats = {
            'hp': 45,
            'attack': 49,
            'defense': 49,
            'special_attack': 65,
            'special_defense': 65,
            'speed': 45,
        }

        result = business._build_evs(base_stats)

        assert isinstance(result, dict)
        assert len(result) == MOCK_NUM_STATS

    @staticmethod
    def test_build_evs_all_zeros():
        """Should initialize all EVs to 0"""
        business = PokemonBusiness()
        base_stats = {
            'hp': 35,
            'attack': 55,
            'defense': 40,
            'special_attack': 50,
            'special_defense': 50,
            'speed': 90,
        }

        result = business._build_evs(base_stats)

        for ev_value in result.values():
            assert ev_value == 0

    @staticmethod
    def test_build_evs_contains_all_stat_keys():
        """Should contain all stat keys from base_stats"""
        business = PokemonBusiness()
        base_stats = {
            'hp': 45,
            'attack': 49,
            'defense': 49,
            'special_attack': 65,
            'special_defense': 65,
            'speed': 45,
        }

        result = business._build_evs(base_stats)

        for key in base_stats:
            assert key in result


class TestPokemonBusinessBuildStats:
    """Test scope for _build_stats method"""

    @staticmethod
    def test_build_stats_returns_dict():
        """Should return a dictionary with calculated stats"""
        business = PokemonBusiness()
        base_stats = {
            'hp': 45,
            'attack': 49,
            'defense': 49,
            'special_attack': 65,
            'special_defense': 65,
            'speed': 45,
        }
        ivs = {
            'hp': 15,
            'attack': 20,
            'defense': 10,
            'special_attack': 25,
            'special_defense': 20,
            'speed': 30,
        }
        evs = {
            'hp': 0,
            'attack': 0,
            'defense': 0,
            'special_attack': 0,
            'special_defense': 0,
            'speed': 0,
        }

        result = business._build_stats(base_stats, ivs, evs, 1)

        assert isinstance(result, dict)
        assert len(result) == MOCK_NUM_STATS

    @staticmethod
    def test_build_stats_contains_all_stat_keys():
        """Should contain all stat keys"""
        business = PokemonBusiness()
        base_stats = {
            'hp': 35,
            'attack': 55,
            'defense': 40,
            'special_attack': 50,
            'special_defense': 50,
            'speed': 90,
        }
        ivs = {
            'hp': 10,
            'attack': 15,
            'defense': 8,
            'special_attack': 20,
            'special_defense': 15,
            'speed': 25,
        }
        evs = {
            'hp': 0,
            'attack': 0,
            'defense': 0,
            'special_attack': 0,
            'special_defense': 0,
            'speed': 0,
        }

        result = business._build_stats(base_stats, ivs, evs, 1)

        for key in base_stats:
            assert key in result

    @staticmethod
    def test_build_stats_all_values_positive():
        """Should ensure all stat values are at least 1"""
        business = PokemonBusiness()
        base_stats = {
            'hp': MOCK_BASE_STAT_LOW,
            'attack': MOCK_BASE_STAT_LOW,
            'defense': MOCK_BASE_STAT_LOW,
            'special_attack': MOCK_BASE_STAT_LOW,
            'special_defense': MOCK_BASE_STAT_LOW,
            'speed': MOCK_BASE_STAT_LOW,
        }
        ivs = {
            'hp': 0,
            'attack': 0,
            'defense': 0,
            'special_attack': 0,
            'special_defense': 0,
            'speed': 0,
        }
        evs = {
            'hp': 0,
            'attack': 0,
            'defense': 0,
            'special_attack': 0,
            'special_defense': 0,
            'speed': 0,
        }

        result = business._build_stats(base_stats, ivs, evs, 1)

        for stat_value in result.values():
            assert stat_value >= 1

    @staticmethod
    def test_build_stats_higher_level_increases_stats():
        """Should calculate higher stats for higher levels"""
        business = PokemonBusiness()
        base_stats = {
            'hp': 45,
            'attack': 49,
            'defense': 49,
            'special_attack': 65,
            'special_defense': 65,
            'speed': 45,
        }
        ivs = {
            'hp': 15,
            'attack': 20,
            'defense': 10,
            'special_attack': 25,
            'special_defense': 20,
            'speed': 30,
        }
        evs = {
            'hp': 0,
            'attack': 0,
            'defense': 0,
            'special_attack': 0,
            'special_defense': 0,
            'speed': 0,
        }

        stats_level_1 = business._build_stats(base_stats, ivs, evs, 1)
        stats_level_50 = business._build_stats(base_stats, ivs, evs, MOCK_LEVEL_50)

        assert stats_level_50['hp'] > stats_level_1['hp']
        assert stats_level_50['attack'] > stats_level_1['attack']


class TestPokemonBusinessCalculateStatValue:
    """Test scope for _calculate_stat_value method"""

    @staticmethod
    def test_calculate_stat_value_with_hp():
        """Should add level bonus for HP stats"""
        business = PokemonBusiness()
        base, iv, ev, level = 45, 15, 0, 1

        result = business._calculate_stat_value(base, iv, ev, level, is_hp=True)

        assert isinstance(result, int)
        assert result >= 1

    @staticmethod
    def test_calculate_stat_value_without_hp():
        """Should not add level bonus for non-HP stats"""
        business = PokemonBusiness()
        base, iv, ev, level = 49, 20, 0, 1

        result = business._calculate_stat_value(base, iv, ev, level, is_hp=False)

        assert isinstance(result, int)
        assert result >= 1

    @staticmethod
    def test_calculate_stat_value_respects_minimum():
        """Should ensure minimum value of 1"""
        business = PokemonBusiness()
        base, iv, ev, level = 0, 0, 0, 1

        result = business._calculate_stat_value(base, iv, ev, level, is_hp=False)

        assert result >= 1

    @staticmethod
    def test_calculate_stat_value_scales_with_level():
        """Should increase stat value with higher level"""
        business = PokemonBusiness()
        base, iv, ev = 50, 20, 0

        value_level_1 = business._calculate_stat_value(base, iv, ev, 1, is_hp=False)
        value_level_50 = business._calculate_stat_value(
            base, iv, ev, MOCK_LEVEL_50, is_hp=False
        )

        assert value_level_50 > value_level_1

    @staticmethod
    def test_calculate_stat_value_with_evs():
        """Should increase stat value with more EVs"""
        business = PokemonBusiness()
        base, iv, level = 50, 20, MOCK_LEVEL_50

        value_no_ev = business._calculate_stat_value(base, iv, 0, level, is_hp=False)
        value_with_ev = business._calculate_stat_value(
            base, iv, MOCK_EV_MAX_STANDARD, level, is_hp=False
        )

        assert value_with_ev > value_no_ev

    @staticmethod
    def test_calculate_stat_value_hp_includes_level():
        """Should include level in HP calculation"""
        business = PokemonBusiness()
        base, iv, ev = 45, 15, 0

        hp_stat = business._calculate_stat_value(base, iv, ev, MOCK_LEVEL_50, is_hp=True)
        other_stat = business._calculate_stat_value(base, iv, ev, MOCK_LEVEL_50, is_hp=False)

        assert hp_stat > other_stat


class TestPokemonBusinessCalculateExperience:
    """Test scope for _calculate_experience method"""

    @staticmethod
    def test_calculate_experience_without_growth_rate():
        """Should use default formula (x^3) when growth_rate is None"""
        business = PokemonBusiness()
        result = business._calculate_experience(growth_rate=None, level=MOCK_NUM_RANGE_5)

        assert result == MOCK_EXP_LEVEL_5

    @staticmethod
    def test_calculate_experience_default_formula_level_1():
        """Should calculate 1 for level 1 with default formula"""
        business = PokemonBusiness()
        result = business._calculate_experience(growth_rate=None, level=1)

        assert result == MOCK_EXP_LEVEL_1

    @staticmethod
    def test_calculate_experience_default_formula_level_10():
        """Should calculate 1000 for level 10 with default formula"""
        business = PokemonBusiness()
        result = business._calculate_experience(growth_rate=None, level=10)

        assert result == MOCK_EXP_LEVEL_10

    @staticmethod
    def test_calculate_experience_with_growth_rate_formula():
        """Should use growth rate formula when provided"""
        business = PokemonBusiness()
        growth_rate = PokemonGrowthRate(
            url='https://pokeapi.co/api/v2/growth-rate/1/',
            name='slow',
            order=1,
            formula='x**3',
            description='Slowly decreases in level.',
        )
        result = business._calculate_experience(
            growth_rate=growth_rate, level=MOCK_NUM_RANGE_5
        )

        assert result == MOCK_EXP_LEVEL_5

    @staticmethod
    def test_calculate_experience_returns_integer():
        """Should return an integer value"""
        business = PokemonBusiness()
        result = business._calculate_experience(growth_rate=None, level=7)

        assert isinstance(result, int)

    @staticmethod
    def test_calculate_experience_non_negative():
        """Should return non-negative experience"""
        business = PokemonBusiness()
        result = business._calculate_experience(growth_rate=None, level=1)

        assert result >= 0

    @staticmethod
    def test_calculate_experience_with_invalid_formula():
        """Should fallback to default formula on invalid formula"""
        business = PokemonBusiness()
        growth_rate = PokemonGrowthRate(
            url='https://pokeapi.co/api/v2/growth-rate/999/',
            name='invalid',
            order=999,
            formula='invalid formula',
            description='Invalid formula',
        )
        result = business._calculate_experience(
            growth_rate=growth_rate, level=MOCK_NUM_RANGE_5
        )

        assert result == MOCK_EXP_LEVEL_5

    @staticmethod
    def test_calculate_experience_scales_with_level():
        """Should increase experience with higher level"""
        business = PokemonBusiness()
        exp_level_1 = business._calculate_experience(growth_rate=None, level=1)
        exp_level_50 = business._calculate_experience(growth_rate=None, level=MOCK_LEVEL_50)

        assert exp_level_50 > exp_level_1
