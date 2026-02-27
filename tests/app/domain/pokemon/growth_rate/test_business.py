from app.domain.pokemon.external.schemas import PokemonExternalLanguage
from app.domain.pokemon.external.schemas.growth_rate import (
    PokemonExternalGrowthRateDescriptionSchemaResponse,
)
from app.domain.pokemon.growth_rate.business import PokemonGrowthRateBusiness

LONG_DESCRIPTION_LENGTH = 1000


class TestPokemonGrowthRateBusinessEnsureDescriptionMessage:
    """Test scope for ensure_description_message method"""

    @staticmethod
    def test_ensure_description_message_with_english_entry():
        """Should return description with English language when available"""
        descriptions = [
            PokemonExternalGrowthRateDescriptionSchemaResponse(
                description='Esta é uma descrição em português',
                language=PokemonExternalLanguage(
                    name='pt', url='https://pokeapi.co/api/v2/language/5/'
                ),
            ),
            PokemonExternalGrowthRateDescriptionSchemaResponse(
                description='This is an English description',
                language=PokemonExternalLanguage(
                    name='en', url='https://pokeapi.co/api/v2/language/9/'
                ),
            ),
            PokemonExternalGrowthRateDescriptionSchemaResponse(
                description='Esta es una descripción en español',
                language=PokemonExternalLanguage(
                    name='es', url='https://pokeapi.co/api/v2/language/7/'
                ),
            ),
        ]

        result = PokemonGrowthRateBusiness.ensure_description_message(descriptions)

        assert isinstance(result, str)
        assert result == 'This is an English description'

    @staticmethod
    def test_ensure_description_message_without_english_entry():
        """Should return first entry when English language is not available"""
        descriptions = [
            PokemonExternalGrowthRateDescriptionSchemaResponse(
                description='Esta é uma descrição em português',
                language=PokemonExternalLanguage(
                    name='pt', url='https://pokeapi.co/api/v2/language/5/'
                ),
            ),
            PokemonExternalGrowthRateDescriptionSchemaResponse(
                description='Esta es una descripción en español',
                language=PokemonExternalLanguage(
                    name='es', url='https://pokeapi.co/api/v2/language/7/'
                ),
            ),
        ]

        result = PokemonGrowthRateBusiness.ensure_description_message(descriptions)

        assert isinstance(result, str)
        assert result == 'Esta é uma descrição em português'

    @staticmethod
    def test_ensure_description_message_with_empty_list():
        """Should return empty string when descriptions list is empty"""
        descriptions = []

        result = PokemonGrowthRateBusiness.ensure_description_message(descriptions)

        assert isinstance(result, str)
        assert not result

    @staticmethod
    def test_ensure_description_message_with_single_entry():
        """Should return the single entry when only one description is available"""
        descriptions = [
            PokemonExternalGrowthRateDescriptionSchemaResponse(
                description='This is the only description available',
                language=PokemonExternalLanguage(
                    name='fr', url='https://pokeapi.co/api/v2/language/4/'
                ),
            ),
        ]

        result = PokemonGrowthRateBusiness.ensure_description_message(descriptions)

        assert isinstance(result, str)
        assert result == 'This is the only description available'

    @staticmethod
    def test_ensure_description_message_preserves_special_characters():
        """Should preserve special characters in description messages"""
        descriptions = [
            PokemonExternalGrowthRateDescriptionSchemaResponse(
                description='A Pokémon\'s "growth rate" determines experience.',
                language=PokemonExternalLanguage(
                    name='en', url='https://pokeapi.co/api/v2/language/9/'
                ),
            ),
        ]

        result = PokemonGrowthRateBusiness.ensure_description_message(descriptions)

        assert result == 'A Pokémon\'s "growth rate" determines experience.'

    @staticmethod
    def test_ensure_description_message_with_long_text():
        """Should handle long description text"""
        long_description = 'A' * LONG_DESCRIPTION_LENGTH
        descriptions = [
            PokemonExternalGrowthRateDescriptionSchemaResponse(
                description=long_description,
                language=PokemonExternalLanguage(
                    name='en', url='https://pokeapi.co/api/v2/language/9/'
                ),
            ),
        ]

        result = PokemonGrowthRateBusiness.ensure_description_message(descriptions)

        assert result == long_description
        assert len(result) == LONG_DESCRIPTION_LENGTH

    @staticmethod
    def test_ensure_description_message_english_priority():
        """Should prioritize English even when not first in list"""
        descriptions = [
            PokemonExternalGrowthRateDescriptionSchemaResponse(
                description='Primera descripción',
                language=PokemonExternalLanguage(
                    name='es', url='https://pokeapi.co/api/v2/language/7/'
                ),
            ),
            PokemonExternalGrowthRateDescriptionSchemaResponse(
                description='Segunda descrição',
                language=PokemonExternalLanguage(
                    name='pt', url='https://pokeapi.co/api/v2/language/5/'
                ),
            ),
            PokemonExternalGrowthRateDescriptionSchemaResponse(
                description='Third description in English',
                language=PokemonExternalLanguage(
                    name='en', url='https://pokeapi.co/api/v2/language/9/'
                ),
            ),
            PokemonExternalGrowthRateDescriptionSchemaResponse(
                description='Quatrième description',
                language=PokemonExternalLanguage(
                    name='fr', url='https://pokeapi.co/api/v2/language/4/'
                ),
            ),
        ]

        result = PokemonGrowthRateBusiness.ensure_description_message(descriptions)

        assert result == 'Third description in English'
