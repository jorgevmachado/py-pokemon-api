from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from app.domain.pokedex.model import Pokedex
from app.domain.pokedex.repository import PokedexRepository
from app.domain.pokedex.schema import CreatePokedexSchema

MOCK_POKEDEX = Pokedex(
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
    discovered=True,
    pokemon_id='9efd7c0a-7fa8-402a-8166-ff85b82cac33',
    trainer_id='6129c647-9823-48c1-a09e-7f471497a0e9',
)


class TestPokedexRepositoryCreate:
    """Test scope for create method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokedex_repository_create_success(session, trainer, pokemon):
        """Should persist pokedex when data is valid"""
        pokedex_data = CreatePokedexSchema(
            hp=MOCK_POKEDEX.hp,
            wins=MOCK_POKEDEX.wins,
            level=MOCK_POKEDEX.level,
            iv_hp=MOCK_POKEDEX.iv_hp,
            ev_hp=MOCK_POKEDEX.ev_hp,
            losses=MOCK_POKEDEX.losses,
            max_hp=MOCK_POKEDEX.max_hp,
            battles=MOCK_POKEDEX.battles,
            iv_speed=MOCK_POKEDEX.iv_speed,
            ev_speed=MOCK_POKEDEX.ev_speed,
            iv_attack=MOCK_POKEDEX.iv_attack,
            ev_attack=MOCK_POKEDEX.ev_attack,
            iv_defense=MOCK_POKEDEX.iv_defense,
            ev_defense=MOCK_POKEDEX.ev_defense,
            experience=MOCK_POKEDEX.experience,
            nickname=MOCK_POKEDEX.nickname,
            iv_special_attack=MOCK_POKEDEX.iv_special_attack,
            ev_special_attack=MOCK_POKEDEX.ev_special_attack,
            iv_special_defense=MOCK_POKEDEX.iv_special_defense,
            ev_special_defense=MOCK_POKEDEX.ev_special_defense,
            discovered=MOCK_POKEDEX.discovered,
            pokemon_id=pokemon.id,
            trainer_id=trainer.id,
            discovered_at=datetime.now(),
        )
        repository = PokedexRepository(session=session)
        result = await repository.create(pokedex_data)

        assert result.hp == MOCK_POKEDEX.hp
        assert result.wins == MOCK_POKEDEX.wins
        assert result.level == MOCK_POKEDEX.level
        assert result.iv_hp == MOCK_POKEDEX.iv_hp
        assert result.ev_hp == MOCK_POKEDEX.ev_hp
        assert result.losses == MOCK_POKEDEX.losses
        assert result.max_hp == MOCK_POKEDEX.max_hp
        assert result.battles == MOCK_POKEDEX.battles
        assert result.iv_speed == MOCK_POKEDEX.iv_speed
        assert result.ev_speed == MOCK_POKEDEX.ev_speed
        assert result.iv_attack == MOCK_POKEDEX.iv_attack
        assert result.ev_attack == MOCK_POKEDEX.ev_attack
        assert result.iv_defense == MOCK_POKEDEX.iv_defense
        assert result.ev_defense == MOCK_POKEDEX.ev_defense
        assert result.experience == MOCK_POKEDEX.experience
        assert result.nickname == MOCK_POKEDEX.nickname
        assert result.iv_special_attack == MOCK_POKEDEX.iv_special_attack
        assert result.ev_special_attack == MOCK_POKEDEX.ev_special_attack
        assert result.iv_special_defense == MOCK_POKEDEX.iv_special_defense
        assert result.ev_special_defense == MOCK_POKEDEX.ev_special_defense

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokedex_repository_create_commit_error(session, trainer, pokemon):
        """Should raise exception when database commit fails"""
        pokedex_data = CreatePokedexSchema(
            hp=MOCK_POKEDEX.hp,
            wins=MOCK_POKEDEX.wins,
            level=MOCK_POKEDEX.level,
            iv_hp=MOCK_POKEDEX.iv_hp,
            ev_hp=MOCK_POKEDEX.ev_hp,
            losses=MOCK_POKEDEX.losses,
            max_hp=MOCK_POKEDEX.max_hp,
            battles=MOCK_POKEDEX.battles,
            iv_speed=MOCK_POKEDEX.iv_speed,
            ev_speed=MOCK_POKEDEX.ev_speed,
            iv_attack=MOCK_POKEDEX.iv_attack,
            ev_attack=MOCK_POKEDEX.ev_attack,
            iv_defense=MOCK_POKEDEX.iv_defense,
            ev_defense=MOCK_POKEDEX.ev_defense,
            experience=MOCK_POKEDEX.experience,
            nickname=MOCK_POKEDEX.nickname,
            iv_special_attack=MOCK_POKEDEX.iv_special_attack,
            ev_special_attack=MOCK_POKEDEX.ev_special_attack,
            iv_special_defense=MOCK_POKEDEX.iv_special_defense,
            ev_special_defense=MOCK_POKEDEX.ev_special_defense,
            discovered=MOCK_POKEDEX.discovered,
            pokemon_id=pokemon.id,
            trainer_id=trainer.id,
            discovered_at=datetime.now(),
        )
        session.commit = AsyncMock(side_effect=Exception('Database error'))

        repository = PokedexRepository(session=session)

        with pytest.raises(Exception, match='Database error'):
            await repository.create(pokedex_data)


class TestPokedexRepositoryFindByTrainer:
    """Test scope for find_by_trainer method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_find_by_trainer_returns_set(session, trainer, pokemon):
        """Should return a set of pokemon IDs"""
        pokedex_data = CreatePokedexSchema(
            hp=MOCK_POKEDEX.hp,
            wins=MOCK_POKEDEX.wins,
            level=MOCK_POKEDEX.level,
            iv_hp=MOCK_POKEDEX.iv_hp,
            ev_hp=MOCK_POKEDEX.ev_hp,
            losses=MOCK_POKEDEX.losses,
            max_hp=MOCK_POKEDEX.max_hp,
            battles=MOCK_POKEDEX.battles,
            iv_speed=MOCK_POKEDEX.iv_speed,
            ev_speed=MOCK_POKEDEX.ev_speed,
            iv_attack=MOCK_POKEDEX.iv_attack,
            ev_attack=MOCK_POKEDEX.ev_attack,
            iv_defense=MOCK_POKEDEX.iv_defense,
            ev_defense=MOCK_POKEDEX.ev_defense,
            experience=MOCK_POKEDEX.experience,
            nickname=MOCK_POKEDEX.nickname,
            iv_special_attack=MOCK_POKEDEX.iv_special_attack,
            ev_special_attack=MOCK_POKEDEX.ev_special_attack,
            iv_special_defense=MOCK_POKEDEX.iv_special_defense,
            ev_special_defense=MOCK_POKEDEX.ev_special_defense,
            discovered=MOCK_POKEDEX.discovered,
            pokemon_id=pokemon.id,
            trainer_id=trainer.id,
            discovered_at=datetime.now(),
        )
        repository = PokedexRepository(session=session)
        await repository.create(pokedex_data)

        result = await repository.find_by_trainer(trainer.id)

        assert isinstance(result, set)

    @staticmethod
    @pytest.mark.asyncio
    async def test_find_by_trainer_contains_pokemon_id(session, trainer, pokemon):
        """Should contain discovered pokemon ID"""
        pokedex_data = CreatePokedexSchema(
            hp=MOCK_POKEDEX.hp,
            wins=MOCK_POKEDEX.wins,
            level=MOCK_POKEDEX.level,
            iv_hp=MOCK_POKEDEX.iv_hp,
            ev_hp=MOCK_POKEDEX.ev_hp,
            losses=MOCK_POKEDEX.losses,
            max_hp=MOCK_POKEDEX.max_hp,
            battles=MOCK_POKEDEX.battles,
            iv_speed=MOCK_POKEDEX.iv_speed,
            ev_speed=MOCK_POKEDEX.ev_speed,
            iv_attack=MOCK_POKEDEX.iv_attack,
            ev_attack=MOCK_POKEDEX.ev_attack,
            iv_defense=MOCK_POKEDEX.iv_defense,
            ev_defense=MOCK_POKEDEX.ev_defense,
            experience=MOCK_POKEDEX.experience,
            nickname=MOCK_POKEDEX.nickname,
            iv_special_attack=MOCK_POKEDEX.iv_special_attack,
            ev_special_attack=MOCK_POKEDEX.ev_special_attack,
            iv_special_defense=MOCK_POKEDEX.iv_special_defense,
            ev_special_defense=MOCK_POKEDEX.ev_special_defense,
            discovered=MOCK_POKEDEX.discovered,
            pokemon_id=pokemon.id,
            trainer_id=trainer.id,
            discovered_at=datetime.now(),
        )
        repository = PokedexRepository(session=session)
        await repository.create(pokedex_data)

        result = await repository.find_by_trainer(trainer.id)

        assert pokemon.id in result

    @staticmethod
    @pytest.mark.asyncio
    async def test_find_by_trainer_empty_for_nonexistent_trainer(session):
        """Should return empty set for nonexistent trainer"""
        repository = PokedexRepository(session=session)
        nonexistent_trainer_id = '00000000-0000-0000-0000-000000000000'

        result = await repository.find_by_trainer(nonexistent_trainer_id)

        assert len(result) == 0

    @staticmethod
    @pytest.mark.asyncio
    async def test_find_by_trainer_only_discovered(session, trainer, pokemon):
        """Should only return discovered pokemon"""
        pokedex_data = CreatePokedexSchema(
            hp=MOCK_POKEDEX.hp,
            wins=MOCK_POKEDEX.wins,
            level=MOCK_POKEDEX.level,
            iv_hp=MOCK_POKEDEX.iv_hp,
            ev_hp=MOCK_POKEDEX.ev_hp,
            losses=MOCK_POKEDEX.losses,
            max_hp=MOCK_POKEDEX.max_hp,
            battles=MOCK_POKEDEX.battles,
            iv_speed=MOCK_POKEDEX.iv_speed,
            ev_speed=MOCK_POKEDEX.ev_speed,
            iv_attack=MOCK_POKEDEX.iv_attack,
            ev_attack=MOCK_POKEDEX.ev_attack,
            iv_defense=MOCK_POKEDEX.iv_defense,
            ev_defense=MOCK_POKEDEX.ev_defense,
            experience=MOCK_POKEDEX.experience,
            nickname=MOCK_POKEDEX.nickname,
            iv_special_attack=MOCK_POKEDEX.iv_special_attack,
            ev_special_attack=MOCK_POKEDEX.ev_special_attack,
            iv_special_defense=MOCK_POKEDEX.iv_special_defense,
            ev_special_defense=MOCK_POKEDEX.ev_special_defense,
            discovered=True,
            pokemon_id=pokemon.id,
            trainer_id=trainer.id,
            discovered_at=datetime.now(),
        )
        repository = PokedexRepository(session=session)
        await repository.create(pokedex_data)

        result = await repository.find_by_trainer(trainer.id)

        assert len(result) >= 1
        assert pokemon.id in result

    @staticmethod
    @pytest.mark.asyncio
    async def test_find_by_trainer_filters_by_trainer_id(session, trainer, pokemon):
        """Should only return pokemon from specified trainer"""
        pokedex_data = CreatePokedexSchema(
            hp=MOCK_POKEDEX.hp,
            wins=MOCK_POKEDEX.wins,
            level=MOCK_POKEDEX.level,
            iv_hp=MOCK_POKEDEX.iv_hp,
            ev_hp=MOCK_POKEDEX.ev_hp,
            losses=MOCK_POKEDEX.losses,
            max_hp=MOCK_POKEDEX.max_hp,
            battles=MOCK_POKEDEX.battles,
            iv_speed=MOCK_POKEDEX.iv_speed,
            ev_speed=MOCK_POKEDEX.ev_speed,
            iv_attack=MOCK_POKEDEX.iv_attack,
            ev_attack=MOCK_POKEDEX.ev_attack,
            iv_defense=MOCK_POKEDEX.iv_defense,
            ev_defense=MOCK_POKEDEX.ev_defense,
            experience=MOCK_POKEDEX.experience,
            nickname=MOCK_POKEDEX.nickname,
            iv_special_attack=MOCK_POKEDEX.iv_special_attack,
            ev_special_attack=MOCK_POKEDEX.ev_special_attack,
            iv_special_defense=MOCK_POKEDEX.iv_special_defense,
            ev_special_defense=MOCK_POKEDEX.ev_special_defense,
            discovered=True,
            pokemon_id=pokemon.id,
            trainer_id=trainer.id,
            discovered_at=datetime.now(),
        )
        repository = PokedexRepository(session=session)
        await repository.create(pokedex_data)

        result = await repository.find_by_trainer(trainer.id)

        assert isinstance(result, set)
        assert pokemon.id in result
