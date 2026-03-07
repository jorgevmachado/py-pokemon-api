from http import HTTPStatus
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from app.domain.battle.schema import (
    BattlePokemonSchema,
    BattleResult,
    BattleSchema,
    GetBattlePokemonSchema,
)
from app.domain.battle.service import PokemonBattleService
from app.domain.move.model import PokemonMove
from app.domain.progression.schema import StatBlock
from tests.factories.pokemon import MOCK_POKEMON_BULBASAUR

MOCK_BATTLE_SCHEMA = BattleSchema(
    id='test-id',
    hp=50,
    wins=0,
    level=10,
    iv_hp=20,
    ev_hp=100,
    losses=0,
    max_hp=60,
    battles=0,
    nickname='test-pokemon',
    speed=45,
    iv_speed=20,
    ev_speed=50,
    attack=50,
    iv_attack=15,
    ev_attack=80,
    defense=49,
    iv_defense=20,
    ev_defense=100,
    experience=100,
    special_attack=65,
    iv_special_attack=25,
    ev_special_attack=60,
    special_defense=65,
    iv_special_defense=20,
    ev_special_defense=80,
    pokemon=MOCK_POKEMON_BULBASAUR,
    formula='x**2',
)

MOCK_MOVE = PokemonMove(
    name='vine-whip',
    type='grass',
    power=45,
    accuracy=100,
    pp=25,
    damage_class='physical',
    url='https://pokeapi.co/api/v2/move/22/',
    order=22,
    target='selected-pokemon',
    effect='This move deals damage',
    priority=0,
    short_effect='Deals damage',
    effect_chance=None,
)


class TestPokemonBattleServiceInit:
    """Test scope for service initialization"""

    @staticmethod
    def test_service_initialization():
        """Should initialize with required dependencies"""
        captured_service = AsyncMock()
        pokedex_service = AsyncMock()
        pokemon_service = AsyncMock()

        service = PokemonBattleService(
            captured_pokemon_service=captured_service,
            pokedex_service=pokedex_service,
            pokemon_service=pokemon_service,
        )

        assert service.pokemon_service == pokemon_service
        assert service.pokedex_service == pokedex_service
        assert service.captured_pokemon_service == captured_service
        assert service.business is not None
        assert service.progression_business is not None
        assert service.business_pokemon_move is not None


class TestPokemonBattleServiceGetTrainerPokemon:
    """Test scope for get_trainer_pokemon method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_get_trainer_pokemon_success():
        """Should return trainer pokemon when found"""
        captured_service = AsyncMock()
        pokedex_service = AsyncMock()
        pokemon_service = AsyncMock()

        mock_captured = MagicMock()
        mock_captured.moves = [MOCK_MOVE]
        captured_service.find_by_pokemon = AsyncMock(return_value=mock_captured)

        service = PokemonBattleService(
            captured_pokemon_service=captured_service,
            pokedex_service=pokedex_service,
            pokemon_service=pokemon_service,
        )
        service.business.convert_captured_pokemon_to_pokemon_stats = MagicMock(
            return_value=MOCK_BATTLE_SCHEMA
        )

        result = await service.get_trainer_pokemon(
            trainer_id='trainer-id',
            pokemon_name='bulbasaur',
            pokemon_move='vine-whip',
        )

        assert isinstance(result, GetBattlePokemonSchema)
        assert result.pokemon == MOCK_BATTLE_SCHEMA
        assert result.pokemon_move == MOCK_MOVE

    @staticmethod
    @pytest.mark.asyncio
    async def test_get_trainer_pokemon_not_found():
        """Should raise HTTPException when pokemon not found"""
        captured_service = AsyncMock()
        pokedex_service = AsyncMock()
        pokemon_service = AsyncMock()

        captured_service.find_by_pokemon = AsyncMock(return_value=None)

        service = PokemonBattleService(
            captured_pokemon_service=captured_service,
            pokedex_service=pokedex_service,
            pokemon_service=pokemon_service,
        )

        with pytest.raises(HTTPException) as exc_info:
            await service.get_trainer_pokemon(
                trainer_id='trainer-id',
                pokemon_name='bulbasaur',
                pokemon_move='vine-whip',
            )

        assert exc_info.value.status_code == HTTPStatus.NOT_FOUND
        assert exc_info.value.detail == 'Trainer Pokemon not found'

    @staticmethod
    @pytest.mark.asyncio
    async def test_get_trainer_pokemon_move_not_found():
        """Should raise HTTPException when move not found"""
        captured_service = AsyncMock()
        pokedex_service = AsyncMock()
        pokemon_service = AsyncMock()

        mock_captured = MagicMock()
        mock_captured.moves = []
        captured_service.find_by_pokemon = AsyncMock(return_value=mock_captured)

        service = PokemonBattleService(
            captured_pokemon_service=captured_service,
            pokedex_service=pokedex_service,
            pokemon_service=pokemon_service,
        )

        with pytest.raises(HTTPException) as exc_info:
            await service.get_trainer_pokemon(
                trainer_id='trainer-id',
                pokemon_name='bulbasaur',
                pokemon_move='vine-whip',
            )

        assert exc_info.value.status_code == HTTPStatus.NOT_FOUND
        assert exc_info.value.detail == 'Move not found in trainer pokemon moves'


class TestPokemonBattleServiceGetOpponentPokemon:
    """Test scope for get_opponent_pokemon method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_get_opponent_pokemon_not_found():
        """Should raise HTTPException when opponent not found"""
        captured_service = AsyncMock()
        pokedex_service = AsyncMock()
        pokemon_service = AsyncMock()

        pokedex_service.find_by_pokemon = AsyncMock(return_value=None)

        service = PokemonBattleService(
            captured_pokemon_service=captured_service,
            pokedex_service=pokedex_service,
            pokemon_service=pokemon_service,
        )

        with pytest.raises(HTTPException) as exc_info:
            await service.get_opponent_pokemon(
                trainer_id='trainer-id',
                pokemon_name='charizard',
            )

        assert exc_info.value.status_code == HTTPStatus.NOT_FOUND
        assert exc_info.value.detail == 'Opponent Pokedex Pokemon not found'

    @staticmethod
    @pytest.mark.asyncio
    async def test_get_opponent_pokemon_discovered():
        """Should return opponent pokemon when already discovered"""
        captured_service = AsyncMock()
        pokedex_service = AsyncMock()
        pokemon_service = AsyncMock()

        mock_pokedex = MagicMock()
        mock_pokedex.discovered = True
        mock_pokedex.pokemon.moves = [MOCK_MOVE]
        pokedex_service.find_by_pokemon = AsyncMock(return_value=mock_pokedex)

        service = PokemonBattleService(
            captured_pokemon_service=captured_service,
            pokedex_service=pokedex_service,
            pokemon_service=pokemon_service,
        )
        service.business.convert_pokedex_to_pokemon_stats = MagicMock(
            return_value=MOCK_BATTLE_SCHEMA
        )

        result = await service.get_opponent_pokemon(
            trainer_id='trainer-id',
            pokemon_name='charizard',
        )

        assert isinstance(result, GetBattlePokemonSchema)
        assert result.pokemon == MOCK_BATTLE_SCHEMA

    @staticmethod
    @pytest.mark.asyncio
    async def test_get_opponent_pokemon_not_discovered():
        """Should discover pokemon when not discovered"""
        captured_service = AsyncMock()
        pokedex_service = AsyncMock()
        pokemon_service = AsyncMock()

        mock_pokedex = MagicMock()
        mock_pokedex.discovered = False
        mock_pokedex.pokemon.moves = [MOCK_MOVE]
        pokedex_service.find_by_pokemon = AsyncMock(return_value=mock_pokedex)

        mock_discovered = MagicMock()
        mock_discovered.pokemon.moves = [MOCK_MOVE]
        pokedex_service.discover = AsyncMock(return_value=mock_discovered)

        service = PokemonBattleService(
            captured_pokemon_service=captured_service,
            pokedex_service=pokedex_service,
            pokemon_service=pokemon_service,
        )
        service.business.convert_pokedex_to_pokemon_stats = MagicMock(
            return_value=MOCK_BATTLE_SCHEMA
        )

        result = await service.get_opponent_pokemon(
            trainer_id='trainer-id',
            pokemon_name='charizard',
        )

        assert isinstance(result, GetBattlePokemonSchema)
        pokedex_service.discover.assert_awaited_once()


class TestPokemonBattleServiceGetOpponentPokemonMove:
    """Test scope for get_opponent_pokemon_move method"""

    @staticmethod
    def test_get_opponent_pokemon_move_random():
        """Should return random move when no move specified"""
        captured_service = AsyncMock()
        pokedex_service = AsyncMock()
        pokemon_service = AsyncMock()

        mock_pokedex = MagicMock()
        mock_pokedex.pokemon.moves = [MOCK_MOVE]

        service = PokemonBattleService(
            captured_pokemon_service=captured_service,
            pokedex_service=pokedex_service,
            pokemon_service=pokemon_service,
        )
        service.business_pokemon_move.select_random_moves = MagicMock(return_value=[MOCK_MOVE])

        result = service.get_opponent_pokemon_move(pokedex=mock_pokedex)

        assert result == MOCK_MOVE

    @staticmethod
    def test_get_opponent_pokemon_move_specific():
        """Should return specific move when found"""
        captured_service = AsyncMock()
        pokedex_service = AsyncMock()
        pokemon_service = AsyncMock()

        mock_pokedex = MagicMock()
        mock_pokedex.pokemon.moves = [MOCK_MOVE]

        service = PokemonBattleService(
            captured_pokemon_service=captured_service,
            pokedex_service=pokedex_service,
            pokemon_service=pokemon_service,
        )

        result = service.get_opponent_pokemon_move(
            pokedex=mock_pokedex,
            pokemon_move='vine-whip',
        )

        assert result == MOCK_MOVE

    @staticmethod
    def test_get_opponent_pokemon_move_fallback():
        """Should return random move when specified move not found"""
        captured_service = AsyncMock()
        pokedex_service = AsyncMock()
        pokemon_service = AsyncMock()

        mock_pokedex = MagicMock()
        mock_pokedex.pokemon.moves = [MOCK_MOVE]

        service = PokemonBattleService(
            captured_pokemon_service=captured_service,
            pokedex_service=pokedex_service,
            pokemon_service=pokemon_service,
        )
        service.business_pokemon_move.select_random_moves = MagicMock(return_value=[MOCK_MOVE])

        result = service.get_opponent_pokemon_move(
            pokedex=mock_pokedex,
            pokemon_move='non-existent-move',
        )

        assert result == MOCK_MOVE


class TestPokemonBattleServiceBattleAttack:
    """Test scope for battle_attack method"""

    @staticmethod
    def test_battle_attack_error():
        """Should raise HTTPException when attack has error"""
        captured_service = AsyncMock()
        pokedex_service = AsyncMock()
        pokemon_service = AsyncMock()

        service = PokemonBattleService(
            captured_pokemon_service=captured_service,
            pokedex_service=pokedex_service,
            pokemon_service=pokemon_service,
        )

        mock_attack_result = MagicMock()
        mock_attack_result.error = True
        mock_attack_result.error_detail = 'Test error'
        service.business.execute_attack = MagicMock(return_value=mock_attack_result)

        with pytest.raises(HTTPException) as exc_info:
            service.battle_attack(
                move=MOCK_MOVE,
                attacker=MOCK_BATTLE_SCHEMA,
                defender=MOCK_BATTLE_SCHEMA,
            )

        assert exc_info.value.status_code == HTTPStatus.BAD_REQUEST
        assert exc_info.value.detail == 'Test error'

    @staticmethod
    def test_battle_attack_success():
        """Should return BattleResult when attack succeeds"""
        captured_service = AsyncMock()
        pokedex_service = AsyncMock()
        pokemon_service = AsyncMock()

        service = PokemonBattleService(
            captured_pokemon_service=captured_service,
            pokedex_service=pokedex_service,
            pokemon_service=pokemon_service,
        )

        mock_attack_result = MagicMock()
        mock_attack_result.error = False
        mock_attack_result.fainted = False
        mock_attack_result.damage = 10
        mock_attack_result.remaining_hp = 40
        mock_attack_result.missed = False
        mock_attack_result.critical = False
        mock_attack_result.stab = False
        mock_attack_result.applied_status = None

        mock_progression = MagicMock()
        mock_progression.level_up = False
        mock_progression.attacker_progression = MOCK_BATTLE_SCHEMA

        service.business.execute_attack = MagicMock(return_value=mock_attack_result)
        service.progression_business.apply_attack_result = MagicMock(
            return_value=mock_progression
        )

        result = service.battle_attack(
            move=MOCK_MOVE,
            attacker=MOCK_BATTLE_SCHEMA,
            defender=MOCK_BATTLE_SCHEMA,
        )
        result_remaining_hp = 40
        result_attack_damage = 10
        assert isinstance(result, BattleResult)
        assert result.attack_damage == result_attack_damage
        assert result.remaining_hp == result_remaining_hp


class TestPokemonBattleServiceBattle:
    """Test scope for battle method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_battle_fainted_opponent():
        """Should handle battle when opponent faints"""
        captured_service = AsyncMock()
        pokedex_service = AsyncMock()
        pokemon_service = AsyncMock()

        service = PokemonBattleService(
            captured_pokemon_service=captured_service,
            pokedex_service=pokedex_service,
            pokemon_service=pokemon_service,
        )

        mock_trainer_result = GetBattlePokemonSchema(
            pokemon=MOCK_BATTLE_SCHEMA,
            pokemon_move=MOCK_MOVE,
        )
        mock_opponent_result = GetBattlePokemonSchema(
            pokemon=MOCK_BATTLE_SCHEMA,
            pokemon_move=MOCK_MOVE,
        )

        service.get_trainer_pokemon = AsyncMock(return_value=mock_trainer_result)
        service.get_opponent_pokemon = AsyncMock(return_value=mock_opponent_result)

        mock_battle_result = BattleResult(
            winner='test-pokemon',
            fainted=True,
            level_up=False,
            missed=False,
            critical=False,
            stab=False,
            attack_damage=50,
            defense_damage=0,
            remaining_hp=0,
            previous_stats=StatBlock(
                hp=50,
                attack=50,
                defense=49,
                speed=45,
                special_attack=65,
                special_defense=65,
            ),
            previous_level=10,
            previous_experience=100,
            current_stats=StatBlock(
                hp=50,
                attack=50,
                defense=49,
                speed=45,
                special_attack=65,
                special_defense=65,
            ),
            current_level=10,
            current_experience=150,
            applied_status=None,
        )

        service.battle_attack = MagicMock(return_value=mock_battle_result)
        pokedex_service.update = AsyncMock()
        captured_service.update = AsyncMock()

        battle_schema = BattlePokemonSchema(
            trainer_pokemon='bulbasaur',
            trainer_pokemon_move='vine-whip',
            opponent_pokemon='charizard',
            opponent_pokemon_move='flare-blitz',
        )

        result = await service.battle(
            trainer=MagicMock(id='trainer-id'),
            battle_pokemon=battle_schema,
        )

        assert result.fainted is True
        captured_service.update.assert_awaited()

    @staticmethod
    @pytest.mark.asyncio
    async def test_battle_not_fainted():
        """Should handle battle when opponent does not faint"""
        captured_service = AsyncMock()
        pokedex_service = AsyncMock()
        pokemon_service = AsyncMock()

        service = PokemonBattleService(
            captured_pokemon_service=captured_service,
            pokedex_service=pokedex_service,
            pokemon_service=pokemon_service,
        )

        mock_trainer_result = GetBattlePokemonSchema(
            pokemon=MOCK_BATTLE_SCHEMA,
            pokemon_move=MOCK_MOVE,
        )
        mock_opponent_result = GetBattlePokemonSchema(
            pokemon=MOCK_BATTLE_SCHEMA,
            pokemon_move=MOCK_MOVE,
        )

        service.get_trainer_pokemon = AsyncMock(return_value=mock_trainer_result)
        service.get_opponent_pokemon = AsyncMock(return_value=mock_opponent_result)

        mock_battle_result = BattleResult(
            winner='IN BATTLE',
            fainted=False,
            level_up=False,
            missed=False,
            critical=False,
            stab=False,
            attack_damage=20,
            defense_damage=0,
            remaining_hp=30,
            previous_stats=StatBlock(
                hp=50,
                attack=50,
                defense=49,
                speed=45,
                special_attack=65,
                special_defense=65,
            ),
            previous_level=10,
            previous_experience=100,
            current_stats=StatBlock(
                hp=50,
                attack=50,
                defense=49,
                speed=45,
                special_attack=65,
                special_defense=65,
            ),
            current_level=10,
            current_experience=120,
            applied_status=None,
        )

        service.battle_attack = MagicMock(return_value=mock_battle_result)
        service.business.convert_pokedex_to_pokemon_stats = MagicMock(
            return_value=MOCK_BATTLE_SCHEMA
        )

        mock_pokedex = MagicMock()
        pokedex_service.update = AsyncMock(return_value=mock_pokedex)

        mock_captured = MagicMock()
        mock_captured.hp = 40
        captured_service.update = AsyncMock(return_value=mock_captured)

        battle_schema = BattlePokemonSchema(
            trainer_pokemon='bulbasaur',
            trainer_pokemon_move='vine-whip',
            opponent_pokemon='charizard',
            opponent_pokemon_move='flare-blitz',
        )

        result = await service.battle(
            trainer=MagicMock(id='trainer-id'),
            battle_pokemon=battle_schema,
        )

        assert result.fainted is False
        pokedex_service.update.assert_awaited()
        captured_service.update.assert_awaited()
