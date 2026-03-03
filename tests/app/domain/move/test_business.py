from unittest.mock import MagicMock

from app.domain.move.business import EffectEntry, PokemonMoveBusiness
from app.domain.move.model import PokemonMove
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


class TestPokemonMoveBusinessSelectRandomMove:
    """Test scope for select_random_move method"""

    @staticmethod
    def test_empty_moves_list():
        """Should return empty list when no moves available"""
        result = PokemonMoveBusiness.select_random_moves([])
        assert result == []

    @staticmethod
    def test_single_move():
        """Should return single move when only one move available"""
        move = MagicMock(spec=PokemonMove)
        moves = [move]
        result = PokemonMoveBusiness.select_random_moves(moves)
        assert result == moves

    @staticmethod
    def test_less_than_max_moves():
        """Should return all moves when pokemon has less than max moves"""
        moves = [MagicMock(spec=PokemonMove, name=f'move_{i}') for i in range(3)]
        total_moves = 4
        total_moves_result = 3
        result = PokemonMoveBusiness.select_random_moves(moves, max_moves=total_moves)

        assert len(result) == total_moves_result
        for move in moves:
            assert move in result

    @staticmethod
    def test_exactly_max_moves():
        """Should return all moves when pokemon has exactly max moves"""
        total_moves = 4
        moves = [MagicMock(spec=PokemonMove, name=f'move_{i}') for i in range(total_moves)]

        result = PokemonMoveBusiness.select_random_moves(moves, max_moves=4)

        assert len(result) == total_moves
        for move in moves:
            assert move in result

    @staticmethod
    def test_more_than_max_moves():
        """Should return random selection when pokemon has more than max moves"""
        moves = [MagicMock(spec=PokemonMove, name=f'move_{i}') for i in range(5)]

        result = PokemonMoveBusiness.select_random_moves(moves, max_moves=4)
        total_moves = 4
        assert len(result) == total_moves
        for move in result:
            assert move in moves

    @staticmethod
    def test_five_moves_returns_four():
        """Should randomly select 4 moves from 5 available"""
        moves = [MagicMock(spec=PokemonMove, name=f'move_{i}') for i in range(5)]

        result = PokemonMoveBusiness.select_random_moves(moves)
        total_moves = 4
        assert len(result) == total_moves
        for move in result:
            assert move in moves

    @staticmethod
    def test_many_moves_respects_max_moves():
        """Should respect max_moves parameter even with many available moves"""
        total_moves = 4
        moves = [MagicMock(spec=PokemonMove, name=f'move_{i}') for i in range(10)]

        result = PokemonMoveBusiness.select_random_moves(moves, max_moves=total_moves)

        assert len(result) == total_moves
        for move in result:
            assert move in moves

    @staticmethod
    def test_randomness():
        """Should return different random subsets across multiple calls"""
        total_moves = 4
        total_range = 6
        total_result_range = 10
        moves = [MagicMock(spec=PokemonMove, name=f'move_{i}') for i in range(total_range)]

        results = [
            PokemonMoveBusiness.select_random_moves(moves, max_moves=total_moves)
            for _ in range(total_result_range)
        ]

        unique_results = [tuple(sorted([id(m) for m in r])) for r in results]
        assert len(set(unique_results)) > 1 or len(moves) <= total_moves
