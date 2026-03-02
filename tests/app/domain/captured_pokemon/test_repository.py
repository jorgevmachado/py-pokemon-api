from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from app.domain.captured_pokemon.model import CapturedPokemon
from app.domain.captured_pokemon.repository import CapturedPokemonRepository
from app.domain.captured_pokemon.schema import CreateCapturedPokemonSchema

MOCK_CAPTURED_POKEMON = CapturedPokemon(
    hp=7,
    wins=0,
    level=1,
    iv_hp=11,
    ev_hp=0,
    losses=0,
    max_hp=7,
    battles=0,
    iv_speed=12,
    ev_speed=0,
    iv_attack=8,
    ev_attack=0,
    iv_defense=2,
    ev_defense=0,
    experience=1,
    nickname='nickname',
    iv_special_attack=9,
    ev_special_attack=0,
    iv_special_defense=19,
    ev_special_defense=0,
    captured_at=datetime.now(),
    pokemon_id='9efd7c0a-7fa8-402a-8166-ff85b82cac33',
    trainer_id='6129c647-9823-48c1-a09e-7f471497a0e9',
)


class TestCapturedPokemonRepositoryCreate:
    """Test scope for create method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_captured_pokemon_repository_create_success(
            captured_pokemon_repository,
            trainer,
            pokemon
    ):
        """Should persist captured pokemon when data is valid"""
        captured_pokemon_data = CreateCapturedPokemonSchema(
            hp=MOCK_CAPTURED_POKEMON.hp,
            wins=MOCK_CAPTURED_POKEMON.wins,
            level=MOCK_CAPTURED_POKEMON.level,
            iv_hp=MOCK_CAPTURED_POKEMON.iv_hp,
            ev_hp=MOCK_CAPTURED_POKEMON.ev_hp,
            losses=MOCK_CAPTURED_POKEMON.losses,
            max_hp=MOCK_CAPTURED_POKEMON.max_hp,
            battles=MOCK_CAPTURED_POKEMON.battles,
            iv_speed=MOCK_CAPTURED_POKEMON.iv_speed,
            ev_speed=MOCK_CAPTURED_POKEMON.ev_speed,
            iv_attack=MOCK_CAPTURED_POKEMON.iv_attack,
            ev_attack=MOCK_CAPTURED_POKEMON.ev_attack,
            iv_defense=MOCK_CAPTURED_POKEMON.iv_defense,
            ev_defense=MOCK_CAPTURED_POKEMON.ev_defense,
            experience=MOCK_CAPTURED_POKEMON.experience,
            nickname=MOCK_CAPTURED_POKEMON.nickname,
            iv_special_attack=MOCK_CAPTURED_POKEMON.iv_special_attack,
            ev_special_attack=MOCK_CAPTURED_POKEMON.ev_special_attack,
            iv_special_defense=MOCK_CAPTURED_POKEMON.iv_special_defense,
            ev_special_defense=MOCK_CAPTURED_POKEMON.ev_special_defense,
            captured_at=MOCK_CAPTURED_POKEMON.captured_at,
            pokemon_id=pokemon.id,
            trainer_id=trainer.id,
        )
        result = await captured_pokemon_repository.create(
            captured_pokemon_data
        )

        assert result.hp == MOCK_CAPTURED_POKEMON.hp
        assert result.wins == MOCK_CAPTURED_POKEMON.wins
        assert result.level == MOCK_CAPTURED_POKEMON.level
        assert result.iv_hp == MOCK_CAPTURED_POKEMON.iv_hp
        assert result.ev_hp == MOCK_CAPTURED_POKEMON.ev_hp
        assert result.losses == MOCK_CAPTURED_POKEMON.losses
        assert result.max_hp == MOCK_CAPTURED_POKEMON.max_hp
        assert result.battles == MOCK_CAPTURED_POKEMON.battles
        assert result.iv_speed == MOCK_CAPTURED_POKEMON.iv_speed
        assert result.ev_speed == MOCK_CAPTURED_POKEMON.ev_speed
        assert result.iv_attack == MOCK_CAPTURED_POKEMON.iv_attack
        assert result.ev_attack == MOCK_CAPTURED_POKEMON.ev_attack
        assert result.iv_defense == MOCK_CAPTURED_POKEMON.iv_defense
        assert result.ev_defense == MOCK_CAPTURED_POKEMON.ev_defense
        assert result.experience == MOCK_CAPTURED_POKEMON.experience
        assert result.nickname == MOCK_CAPTURED_POKEMON.nickname
        assert result.iv_special_attack == MOCK_CAPTURED_POKEMON.iv_special_attack
        assert result.ev_special_attack == MOCK_CAPTURED_POKEMON.ev_special_attack
        assert result.iv_special_defense == MOCK_CAPTURED_POKEMON.iv_special_defense
        assert result.ev_special_defense == MOCK_CAPTURED_POKEMON.ev_special_defense

    @staticmethod
    @pytest.mark.asyncio
    async def test_captured_pokemon_repository_create_commit_error(
            captured_pokemon_repository,
            session,
            trainer,
            pokemon
    ):
        """Should raise exception when database commit fails"""
        captured_pokemon_data = CreateCapturedPokemonSchema(
            hp=MOCK_CAPTURED_POKEMON.hp,
            wins=MOCK_CAPTURED_POKEMON.wins,
            level=MOCK_CAPTURED_POKEMON.level,
            iv_hp=MOCK_CAPTURED_POKEMON.iv_hp,
            ev_hp=MOCK_CAPTURED_POKEMON.ev_hp,
            losses=MOCK_CAPTURED_POKEMON.losses,
            max_hp=MOCK_CAPTURED_POKEMON.max_hp,
            battles=MOCK_CAPTURED_POKEMON.battles,
            iv_speed=MOCK_CAPTURED_POKEMON.iv_speed,
            ev_speed=MOCK_CAPTURED_POKEMON.ev_speed,
            iv_attack=MOCK_CAPTURED_POKEMON.iv_attack,
            ev_attack=MOCK_CAPTURED_POKEMON.ev_attack,
            iv_defense=MOCK_CAPTURED_POKEMON.iv_defense,
            ev_defense=MOCK_CAPTURED_POKEMON.ev_defense,
            experience=MOCK_CAPTURED_POKEMON.experience,
            nickname=MOCK_CAPTURED_POKEMON.nickname,
            iv_special_attack=MOCK_CAPTURED_POKEMON.iv_special_attack,
            ev_special_attack=MOCK_CAPTURED_POKEMON.ev_special_attack,
            iv_special_defense=MOCK_CAPTURED_POKEMON.iv_special_defense,
            ev_special_defense=MOCK_CAPTURED_POKEMON.ev_special_defense,
            captured_at=MOCK_CAPTURED_POKEMON.captured_at,
            pokemon_id=pokemon.id,
            trainer_id=trainer.id,
        )
        session.commit = AsyncMock(side_effect=Exception('Database error'))

        with pytest.raises(Exception, match='Database error'):
            await captured_pokemon_repository.create(
                captured_pokemon_data
            )
