from app.domain.move.business import EffectEntry, PokemonMoveBusiness
from app.domain.pokemon.external.schemas import (
    PokemonExternalLanguage,
    PokemonExternalMoveEffectEntriesSchemaResponse,
)


class TestPokemonMoveBusinessEnsureEffectMessage:
    """Test scope for ensure_effect_message method"""

    @staticmethod
    def test_ensure_effect_message_with_english_entry():
        """Should return effect entry with English language when available"""
        effect_entries = [
            PokemonExternalMoveEffectEntriesSchemaResponse(
                effect='This is a portuguese effect',
                language=PokemonExternalLanguage(
                    name='pt', url='https://pokeapi.co/api/v2/language/5/'
                ),
                short_effect='Portuguese effect short',
            ),
            PokemonExternalMoveEffectEntriesSchemaResponse(
                effect='This is an english effect',
                language=PokemonExternalLanguage(
                    name='en', url='https://pokeapi.co/api/v2/language/9/'
                ),
                short_effect='English effect short',
            ),
            PokemonExternalMoveEffectEntriesSchemaResponse(
                effect='This is a spanish effect',
                language=PokemonExternalLanguage(
                    name='es', url='https://pokeapi.co/api/v2/language/7/'
                ),
                short_effect='Spanish effect short',
            ),
        ]

        result = PokemonMoveBusiness.ensure_effect_message(effect_entries)

        assert isinstance(result, EffectEntry)
        assert result.effect == 'This is an english effect'
        assert result.short_effect == 'English effect short'

    @staticmethod
    def test_ensure_effect_message_without_english_entry():
        """Should return first entry when English language is not available"""
        effect_entries = [
            PokemonExternalMoveEffectEntriesSchemaResponse(
                effect='This is a portuguese effect',
                language=PokemonExternalLanguage(
                    name='pt', url='https://pokeapi.co/api/v2/language/5/'
                ),
                short_effect='Portuguese effect short',
            ),
            PokemonExternalMoveEffectEntriesSchemaResponse(
                effect='This is a spanish effect',
                language=PokemonExternalLanguage(
                    name='es', url='https://pokeapi.co/api/v2/language/7/'
                ),
                short_effect='Spanish effect short',
            ),
        ]

        result = PokemonMoveBusiness.ensure_effect_message(effect_entries)

        assert isinstance(result, EffectEntry)
        assert result.effect == 'This is a portuguese effect'
        assert result.short_effect == 'Portuguese effect short'

    @staticmethod
    def test_ensure_effect_message_with_empty_list():
        """Should return effect entry with empty strings when effect_entries list is empty"""
        effect_entries = []

        result = PokemonMoveBusiness.ensure_effect_message(effect_entries)

        assert isinstance(result, EffectEntry)
        assert not result.effect
        assert not result.short_effect

    @staticmethod
    def test_ensure_effect_message_with_single_entry():
        """Should return the single entry when only one effect entry is available"""
        effect_entries = [
            PokemonExternalMoveEffectEntriesSchemaResponse(
                effect='This is the only effect',
                language=PokemonExternalLanguage(
                    name='fr', url='https://pokeapi.co/api/v2/language/4/'
                ),
                short_effect='Only effect short',
            ),
        ]

        result = PokemonMoveBusiness.ensure_effect_message(effect_entries)

        assert isinstance(result, EffectEntry)
        assert result.effect == 'This is the only effect'
        assert result.short_effect == 'Only effect short'

    @staticmethod
    def test_ensure_effect_message_preserves_special_characters():
        """Should preserve special characters in effect messages"""
        effect_entries = [
            PokemonExternalMoveEffectEntriesSchemaResponse(
                effect='Raises the trainer\'s "Special" stat by 1 stage.',
                language=PokemonExternalLanguage(
                    name='en', url='https://pokeapi.co/api/v2/language/9/'
                ),
                short_effect='Raises Sp. Atk by 1.',
            ),
        ]

        result = PokemonMoveBusiness.ensure_effect_message(effect_entries)

        assert isinstance(result, EffectEntry)
        assert result.effect == 'Raises the trainer\'s "Special" stat by 1 stage.'
        assert result.short_effect == 'Raises Sp. Atk by 1.'

    @staticmethod
    def test_ensure_effect_message_with_long_text():
        """Should handle long effect and short_effect text"""
        total_result_effect = 1000
        total_result_short_effect = 500
        long_effect = 'A' * total_result_effect
        long_short_effect = 'B' * total_result_short_effect
        effect_entries = [
            PokemonExternalMoveEffectEntriesSchemaResponse(
                effect=long_effect,
                language=PokemonExternalLanguage(
                    name='en', url='https://pokeapi.co/api/v2/language/9/'
                ),
                short_effect=long_short_effect,
            ),
        ]

        result = PokemonMoveBusiness.ensure_effect_message(effect_entries)

        assert result.effect == long_effect
        assert result.short_effect == long_short_effect
        assert len(result.effect) == total_result_effect
        assert len(result.short_effect) == total_result_short_effect
