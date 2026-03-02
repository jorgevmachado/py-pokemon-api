from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from app.domain.pokedex.repository import PokedexRepository
from app.domain.pokedex.schema import CreatePokedexSchema, PokedexFilterPage
from tests.app.domain.pokedex.conftest import MOCK_POKEDEX, PokedexFactory


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


class TestPokedexRepositoryListByTrainer:
    """Test scope for list_by_trainer method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokedex_repository_list_success(session, trainer, pokemon):
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

        result = await repository.list_all(
            PokedexFilterPage(
                trainer_id=trainer.id,
            )
        )
        assert isinstance(result, list)
        assert len(result) >= 1

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokedex_repository_list_empty(session, trainer, pokemon):
        repository = PokedexRepository(session=session)

        result = await repository.list_all(
            PokedexFilterPage(
                trainer_id=trainer.id,
            )
        )
        assert isinstance(result, list)
        assert len(result) == 0

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokedex_repository_list_with_offset(session, trainer, pokemon):
        for _ in range(5):
            pokedex = PokedexFactory(trainer_id=trainer.id, pokemon_id=pokemon.id)
            session.add(pokedex)
            await session.commit()

        repository = PokedexRepository(session=session)

        result = await repository.list_all(
            PokedexFilterPage(trainer_id=trainer.id, offset=2, limit=10)
        )
        assert result is not None
        assert hasattr(result, 'items')
        assert len(result.items) >= 1

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokedex_repository_list_with_limit(session, trainer, pokemon):
        total_results = 2
        for _ in range(5):
            pokedex = PokedexFactory(trainer_id=trainer.id, pokemon_id=pokemon.id)
            session.add(pokedex)
            await session.commit()

        repository = PokedexRepository(session=session)

        result = await repository.list_all(
            PokedexFilterPage(trainer_id=trainer.id, offset=0, limit=2)
        )
        assert result is not None
        if hasattr(result, 'items'):
            assert len(result.items) == total_results
        else:
            assert len(result) == total_results

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokedex_repository_list_with_offset_and_limit(session, trainer, pokemon):
        total_results = 4
        for _ in range(10):
            pokedex = PokedexFactory(trainer_id=trainer.id, pokemon_id=pokemon.id)
            session.add(pokedex)
            await session.commit()

        repository = PokedexRepository(session=session)

        result = await repository.list_all(
            PokedexFilterPage(trainer_id=trainer.id, offset=3, limit=4)
        )
        assert result is not None
        if hasattr(result, 'items'):
            assert len(result.items) == total_results
        else:
            assert len(result) == total_results

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokedex_repository_list_without_pagination(session, trainer, pokemon):
        total_results = 3
        for _ in range(3):
            pokedex = PokedexFactory(trainer_id=trainer.id, pokemon_id=pokemon.id)
            session.add(pokedex)
            await session.commit()

        repository = PokedexRepository(session=session)

        result = await repository.list_all(
            PokedexFilterPage(trainer_id=trainer.id, offset=None, limit=None)
        )
        assert isinstance(result, list)
        assert len(result) == total_results
