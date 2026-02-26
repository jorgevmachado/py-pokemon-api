from app.domain.pokemon.business import PokemonBusiness
from app.domain.pokemon.external.schemas import (
    PokemonExternalBase,
)
from app.domain.pokemon.external.schemas.evolution import (
    PokemonExternalEvolutionChainEvolvesToSchemaResponse,
    PokemonExternalEvolutionChainSchemaResponse,
)


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
