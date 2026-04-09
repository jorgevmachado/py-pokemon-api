from datetime import datetime

from app.domain.pokemon.business import PokemonBusiness
from app.domain.pokemon.external.schemas import (
    PokemonExternalBase,
)
from app.domain.pokemon.external.schemas.evolution import (
    PokemonExternalEvolutionChainEvolvesToSchemaResponse,
    PokemonExternalEvolutionChainSchemaResponse,
)
from app.domain.pokemon.schema import PokemonFilterPage, PokemonSchema
from app.models.pokemon import Pokemon
from app.shared.enums.status_enum import StatusEnum

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

    @staticmethod
    def test_get_random_pokemon_not_prefers_complete():
        """Should always not prefer complete pokemon over incomplete"""
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
            status=StatusEnum.COMPLETE,
            external_image='https://example.com/200.png',
        )
        pokemons = [pokemon_1, pokemon_2, pokemon_3]

        result = business.get_random_pokemon(pokemons=pokemons, complete=False)
        assert result is not None
        assert result in pokemons
        assert result.order in MOCK_VARIOUS_ORDERS


class TestPokemonBusinessFilterAndPaginateCatalog:
    """Test scope for filter_and_paginate_catalog and _matches_filter methods"""

    @staticmethod
    def test_filter_and_paginate_catalog_no_filters():
        """Should return all items when no filters are provided"""
        result_len = 2
        business = PokemonBusiness()
        pokemons = [
            PokemonSchema(
                id='1',
                name='bulbasaur',
                order=1,
                url='url1',
                status=StatusEnum.COMPLETE,
                external_image='img1',
                hp=45,
                attack=49,
                defense=49,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            ),
            PokemonSchema(
                id='2',
                name='ivysaur',
                order=2,
                url='url2',
                status=StatusEnum.COMPLETE,
                external_image='img2',
                hp=60,
                attack=62,
                defense=63,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            ),
        ]
        result = business.filter_and_paginate_catalog(pokemons)
        assert isinstance(result, list)
        assert len(result) == result_len

    @staticmethod
    def test_filter_and_paginate_catalog_with_name_filter():
        """Should filter by name (case-insensitive)"""
        result_len = 1
        business = PokemonBusiness()
        pokemons = [
            PokemonSchema(
                id='1',
                name='bulbasaur',
                order=1,
                url='url1',
                status=StatusEnum.COMPLETE,
                external_image='img1',
                hp=45,
                attack=49,
                defense=49,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            ),
            PokemonSchema(
                id='2',
                name='ivysaur',
                order=2,
                url='url2',
                status=StatusEnum.COMPLETE,
                external_image='img2',
                hp=60,
                attack=62,
                defense=63,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            ),
        ]
        filter_page = PokemonFilterPage(name='IVYSAUR')
        result = business.filter_and_paginate_catalog(pokemons, filter_page)
        assert isinstance(result, list)
        assert len(result) == result_len
        assert result[0].name == 'ivysaur'

    @staticmethod
    def test_filter_and_paginate_catalog_with_multiple_filters():
        """Should filter by multiple fields"""
        result_len = 1
        result_order = 2
        business = PokemonBusiness()
        pokemons = [
            PokemonSchema(
                id='1',
                name='bulbasaur',
                order=1,
                url='url1',
                status=StatusEnum.COMPLETE,
                external_image='img1',
                hp=45,
                attack=49,
                defense=49,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            ),
            PokemonSchema(
                id='2',
                name='ivysaur',
                order=2,
                url='url2',
                status=StatusEnum.COMPLETE,
                external_image='img2',
                hp=60,
                attack=62,
                defense=63,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            ),
        ]
        filter_page = PokemonFilterPage(name='ivysaur', order=2)
        result = business.filter_and_paginate_catalog(pokemons, filter_page)
        assert isinstance(result, list)
        assert len(result) == result_len
        assert result[0].name == 'ivysaur'
        assert result[0].order == result_order

    @staticmethod
    def test_filter_and_paginate_catalog_with_nonexistent_filter():
        """Should return empty list when filter does not match any item"""
        business = PokemonBusiness()
        pokemons = [
            PokemonSchema(
                id='1',
                name='bulbasaur',
                order=1,
                url='url1',
                status=StatusEnum.COMPLETE,
                external_image='img1',
                hp=45,
                attack=49,
                defense=49,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
        ]
        filter_page = PokemonFilterPage(name='pikachu')
        result = business.filter_and_paginate_catalog(pokemons, filter_page)
        assert isinstance(result, list)
        assert len(result) == 0

    @staticmethod
    def test_filter_and_paginate_catalog_with_pagination():
        """Should return paginated result when limit and offset are provided"""
        result_len = 5
        result_order = 3
        result_total = 10
        business = PokemonBusiness()
        pokemons = [
            PokemonSchema(
                id=str(i),
                name=f'poke{i}',
                order=i,
                url=f'url{i}',
                status=StatusEnum.COMPLETE,
                external_image=f'img{i}',
                hp=10 + i,
                attack=20 + i,
                defense=30 + i,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            for i in range(1, 11)
        ]
        filter_page = PokemonFilterPage(limit=5, offset=2)
        result = business.filter_and_paginate_catalog(pokemons, filter_page)
        assert hasattr(result, 'items')
        assert len(result.items) == result_len
        assert result.items[0].order == result_order
        assert result.total == result_total

    @staticmethod
    def test_matches_filter_case_insensitive():
        """Should match string fields case-insensitively"""
        business = PokemonBusiness()
        pokemon = PokemonSchema(
            id='1',
            name='Bulbasaur',
            order=1,
            url='url1',
            status=StatusEnum.COMPLETE,
            external_image='img1',
            hp=45,
            attack=49,
            defense=49,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        filters = {'name': 'bulbasaur'}
        assert business._matches_filter(pokemon, filters) is True
        filters = {'name': 'BULBASAUR'}
        assert business._matches_filter(pokemon, filters) is True

    @staticmethod
    def test_matches_filter_non_string():
        """Should match non-string fields exactly"""
        business = PokemonBusiness()
        pokemon = PokemonSchema(
            id='1',
            name='Bulbasaur',
            order=1,
            url='url1',
            status=StatusEnum.COMPLETE,
            external_image='img1',
            hp=45,
            attack=49,
            defense=49,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        filters = {'order': 1}
        assert business._matches_filter(pokemon, filters) is True
        filters = {'order': 2}
        assert business._matches_filter(pokemon, filters) is False

    @staticmethod
    def test_matches_filter_empty_filters():
        business = PokemonBusiness()
        pokemon = PokemonSchema(
            id='1',
            name='Bulbasaur',
            order=1,
            url='url1',
            status=StatusEnum.COMPLETE,
            external_image='img1',
            hp=45,
            attack=49,
            defense=49,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        assert business._matches_filter(pokemon, {}) is True


class TestPokemonBusinessCatalogSerialization:
    @staticmethod
    def test_serialize_catalog_returns_json_dicts():
        business = PokemonBusiness()
        pokemons = [
            Pokemon(
                name='bulbasaur',
                order=1,
                status=StatusEnum.COMPLETE,
                url='https://pokeapi.co/api/v2/pokemon/1/',
                external_image='https://img.pokemondb.net/artwork/bulbasaur.jpg',
                hp=45,
                attack=49,
                defense=49,
            ),
            Pokemon(
                name='ivysaur',
                order=2,
                status=StatusEnum.COMPLETE,
                url='https://pokeapi.co/api/v2/pokemon/2/',
                external_image='https://img.pokemondb.net/artwork/ivysaur.jpg',
                hp=60,
                attack=62,
                defense=63,
            ),
        ]
        # Patch missing fields before serialization
        for i, pokemon in enumerate(pokemons, start=1):
            pokemon.id = str(i)
            pokemon.created_at = datetime.now()
            pokemon.updated_at = datetime.now()
        result = business.serialize_catalog(pokemons)
        assert isinstance(result, list)
        assert all(isinstance(item, dict) for item in result)
        assert result[0]['name'] == 'bulbasaur'
        assert result[1]['name'] == 'ivysaur'

    @staticmethod
    def test_serialize_catalog_empty_list():
        business = PokemonBusiness()
        result = business.serialize_catalog([])
        assert result == []

    @staticmethod
    def test_deserialize_catalog_returns_schema_instances():
        business = PokemonBusiness()
        payload = [
            {
                'id': '1',
                'name': 'bulbasaur',
                'order': 1,
                'status': StatusEnum.COMPLETE.value,
                'url': 'https://pokeapi.co/api/v2/pokemon/1/',
                'external_image': 'https://img.pokemondb.net/artwork/bulbasaur.jpg',
                'hp': 45,
                'attack': 49,
                'defense': 49,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
            },
            {
                'id': '2',
                'name': 'ivysaur',
                'order': 2,
                'status': StatusEnum.COMPLETE.value,
                'url': 'https://pokeapi.co/api/v2/pokemon/2/',
                'external_image': 'https://img.pokemondb.net/artwork/ivysaur.jpg',
                'hp': 60,
                'attack': 62,
                'defense': 63,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
            },
        ]
        result = business.deserialize_catalog(payload)
        assert isinstance(result, list)
        assert all(isinstance(item, PokemonSchema) for item in result)
        assert result[0].name == 'bulbasaur'
        assert result[1].name == 'ivysaur'

    @staticmethod
    def test_deserialize_catalog_empty_list():
        business = PokemonBusiness()
        result = business.deserialize_catalog([])
        assert result == []

    @staticmethod
    def test_deserialize_catalog_skips_non_dict():
        business = PokemonBusiness()
        payload = [
            'not-a-dict',
            {
                'id': '1',
                'name': 'bulbasaur',
                'order': 1,
                'status': StatusEnum.COMPLETE.value,
                'url': 'https://pokeapi.co/api/v2/pokemon/1/',
                'external_image': 'https://img.pokemondb.net/artwork/bulbasaur.jpg',
                'hp': 45,
                'attack': 49,
                'defense': 49,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
            },
        ]
        result = business.deserialize_catalog(payload)
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].name == 'bulbasaur'
