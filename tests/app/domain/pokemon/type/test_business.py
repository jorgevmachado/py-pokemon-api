from app.domain.pokemon.external.schemas import (
    PokemonExternalBase,
    PokemonExternalBaseTypeSchemaResponse,
)
from app.domain.pokemon.type.business import PokemonTypeBusiness


class TestPokemonTypeBusinessEnsureColors:
    @staticmethod
    def test_pokemon_type_business_ensure_colors_default():
        response_pokemon_type = PokemonExternalBaseTypeSchemaResponse(
            slot=1,
            type=PokemonExternalBase(name='default', url='https://pokeapi.co/api/v2/type/12/'),
        )
        result = PokemonTypeBusiness.ensure_colors(response_pokemon_type)

        assert result.id == 0
        assert result.name == 'default'
        assert result.text_color == '#fff'
        assert result.background_color == '#000'

    @staticmethod
    def test_pokemon_type_business_ensure_colors_success():
        response_pokemon_type = PokemonExternalBaseTypeSchemaResponse(
            slot=1,
            type=PokemonExternalBase(name='ice', url='https://pokeapi.co/api/v2/type/12/'),
        )

        result = PokemonTypeBusiness.ensure_colors(response_pokemon_type)
        assert result.id == 1
        assert result.name == 'ice'
        assert result.text_color == '#fff'
        assert result.background_color == '#51c4e7'
