from app.domain.pokemon.external.schemas import (
    PokemonExternalBase,
    PokemonExternalTypeDamageRelationsSchemaResponse,
)
from app.domain.type.business import PokemonTypeBusiness


class TestPokemonTypeBusinessEnsureColors:
    @staticmethod
    def test_pokemon_type_business_ensure_colors_default():
        result = PokemonTypeBusiness.ensure_colors(pokemon_type='default')

        assert result.id == 0
        assert result.name == 'default'
        assert result.text_color == '#fff'
        assert result.background_color == '#000'

    @staticmethod
    def test_pokemon_type_business_ensure_colors_success():
        result = PokemonTypeBusiness.ensure_colors(pokemon_type='ice')
        assert result.id == 1
        assert result.name == 'ice'
        assert result.text_color == '#fff'
        assert result.background_color == '#51c4e7'


class TestPokemonTypeBusinessEnsureDamageRelations:
    @staticmethod
    def test_pokemon_type_business_ensure_relations_empty():
        response_pokemon_type_damage_relations = (
            PokemonExternalTypeDamageRelationsSchemaResponse(
                double_damage_from=[],
                double_damage_to=[],
                half_damage_from=[],
                half_damage_to=[],
            )
        )
        weakness: list[PokemonExternalBase] = []
        strengths: list[PokemonExternalBase] = []

        result = PokemonTypeBusiness.ensure_damage_relations(
            response_pokemon_type_damage_relations
        )

        assert len(result.weakness) == len(weakness)
        assert len(result.strengths) == len(strengths)

    @staticmethod
    def test_pokemon_type_business_ensure_relations_success():
        response_pokemon_type_damage_relations = (
            PokemonExternalTypeDamageRelationsSchemaResponse(
                double_damage_from=[
                    PokemonExternalBase(
                        name='ground', url='https://pokeapi.co/api/v2/type/5/'
                    ),
                    PokemonExternalBase(name='rock', url='https://pokeapi.co/api/v2/type/6/'),
                ],
                double_damage_to=[
                    PokemonExternalBase(name='bug', url='https://pokeapi.co/api/v2/type/7/'),
                    PokemonExternalBase(name='steel', url='https://pokeapi.co/api/v2/type/9/'),
                ],
                half_damage_from=[
                    PokemonExternalBase(name='bug', url='https://pokeapi.co/api/v2/type/7/'),
                    PokemonExternalBase(name='steel', url='https://pokeapi.co/api/v2/type/9/'),
                ],
                half_damage_to=[
                    PokemonExternalBase(name='fire', url='https://pokeapi.co/api/v2/type/10/'),
                ],
            )
        )
        weakness: list[PokemonExternalBase] = [
            PokemonExternalBase(name='ground', url='https://pokeapi.co/api/v2/type/5/'),
            PokemonExternalBase(name='rock', url='https://pokeapi.co/api/v2/type/6/'),
            PokemonExternalBase(name='bug', url='https://pokeapi.co/api/v2/type/7/'),
            PokemonExternalBase(name='steel', url='https://pokeapi.co/api/v2/type/9/'),
        ]
        strengths: list[PokemonExternalBase] = [
            PokemonExternalBase(name='bug', url='https://pokeapi.co/api/v2/type/7/'),
            PokemonExternalBase(name='steel', url='https://pokeapi.co/api/v2/type/9/'),
            PokemonExternalBase(name='fire', url='https://pokeapi.co/api/v2/type/10/'),
        ]

        result = PokemonTypeBusiness.ensure_damage_relations(
            response_pokemon_type_damage_relations
        )

        assert len(result.weakness) == len(weakness)
        assert len(result.strengths) == len(strengths)
