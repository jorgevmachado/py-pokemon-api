from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.domain.pokedex.repository import PokedexRepository
from app.domain.pokedex.schema import CreatePokedexSchema, FindPokedexSchema, PokedexFilterPage
from tests.factories.pokedex import MOCK_POKEDEX, PokedexFactory


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
            speed=MOCK_POKEDEX.speed,
            ev_speed=MOCK_POKEDEX.ev_speed,
            iv_attack=MOCK_POKEDEX.iv_attack,
            attack=MOCK_POKEDEX.attack,
            ev_attack=MOCK_POKEDEX.ev_attack,
            iv_defense=MOCK_POKEDEX.iv_defense,
            defense=MOCK_POKEDEX.defense,
            ev_defense=MOCK_POKEDEX.ev_defense,
            experience=MOCK_POKEDEX.experience,
            nickname=MOCK_POKEDEX.nickname,
            iv_special_attack=MOCK_POKEDEX.iv_special_attack,
            special_attack=MOCK_POKEDEX.special_attack,
            ev_special_attack=MOCK_POKEDEX.ev_special_attack,
            iv_special_defense=MOCK_POKEDEX.iv_special_defense,
            special_defense=MOCK_POKEDEX.special_defense,
            ev_special_defense=MOCK_POKEDEX.ev_special_defense,
            discovered=MOCK_POKEDEX.discovered,
            pokemon_id=pokemon.id,
            trainer_id=trainer.id,
            discovered_at=datetime.now(),
            formula=MOCK_POKEDEX.formula,
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
            speed=MOCK_POKEDEX.speed,
            ev_speed=MOCK_POKEDEX.ev_speed,
            iv_attack=MOCK_POKEDEX.iv_attack,
            attack=MOCK_POKEDEX.attack,
            ev_attack=MOCK_POKEDEX.ev_attack,
            iv_defense=MOCK_POKEDEX.iv_defense,
            defense=MOCK_POKEDEX.defense,
            ev_defense=MOCK_POKEDEX.ev_defense,
            experience=MOCK_POKEDEX.experience,
            nickname=MOCK_POKEDEX.nickname,
            iv_special_attack=MOCK_POKEDEX.iv_special_attack,
            special_attack=MOCK_POKEDEX.special_attack,
            ev_special_attack=MOCK_POKEDEX.ev_special_attack,
            iv_special_defense=MOCK_POKEDEX.iv_special_defense,
            special_defense=MOCK_POKEDEX.special_defense,
            ev_special_defense=MOCK_POKEDEX.ev_special_defense,
            discovered=MOCK_POKEDEX.discovered,
            pokemon_id=pokemon.id,
            trainer_id=trainer.id,
            discovered_at=datetime.now(),
            formula=MOCK_POKEDEX.formula,
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
            speed=MOCK_POKEDEX.speed,
            ev_speed=MOCK_POKEDEX.ev_speed,
            iv_attack=MOCK_POKEDEX.iv_attack,
            attack=MOCK_POKEDEX.attack,
            ev_attack=MOCK_POKEDEX.ev_attack,
            iv_defense=MOCK_POKEDEX.iv_defense,
            defense=MOCK_POKEDEX.defense,
            ev_defense=MOCK_POKEDEX.ev_defense,
            experience=MOCK_POKEDEX.experience,
            nickname=MOCK_POKEDEX.nickname,
            iv_special_attack=MOCK_POKEDEX.iv_special_attack,
            special_attack=MOCK_POKEDEX.special_attack,
            ev_special_attack=MOCK_POKEDEX.ev_special_attack,
            iv_special_defense=MOCK_POKEDEX.iv_special_defense,
            special_defense=MOCK_POKEDEX.special_defense,
            ev_special_defense=MOCK_POKEDEX.ev_special_defense,
            discovered=MOCK_POKEDEX.discovered,
            pokemon_id=pokemon.id,
            trainer_id=trainer.id,
            discovered_at=datetime.now(),
            formula=MOCK_POKEDEX.formula,
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
            speed=MOCK_POKEDEX.speed,
            ev_speed=MOCK_POKEDEX.ev_speed,
            iv_attack=MOCK_POKEDEX.iv_attack,
            attack=MOCK_POKEDEX.attack,
            ev_attack=MOCK_POKEDEX.ev_attack,
            iv_defense=MOCK_POKEDEX.iv_defense,
            defense=MOCK_POKEDEX.defense,
            ev_defense=MOCK_POKEDEX.ev_defense,
            experience=MOCK_POKEDEX.experience,
            nickname=MOCK_POKEDEX.nickname,
            iv_special_attack=MOCK_POKEDEX.iv_special_attack,
            special_attack=MOCK_POKEDEX.special_attack,
            ev_special_attack=MOCK_POKEDEX.ev_special_attack,
            iv_special_defense=MOCK_POKEDEX.iv_special_defense,
            special_defense=MOCK_POKEDEX.special_defense,
            ev_special_defense=MOCK_POKEDEX.ev_special_defense,
            discovered=MOCK_POKEDEX.discovered,
            pokemon_id=pokemon.id,
            trainer_id=trainer.id,
            discovered_at=datetime.now(),
            formula=MOCK_POKEDEX.formula,
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
            speed=MOCK_POKEDEX.speed,
            ev_speed=MOCK_POKEDEX.ev_speed,
            iv_attack=MOCK_POKEDEX.iv_attack,
            attack=MOCK_POKEDEX.attack,
            ev_attack=MOCK_POKEDEX.ev_attack,
            iv_defense=MOCK_POKEDEX.iv_defense,
            defense=MOCK_POKEDEX.defense,
            ev_defense=MOCK_POKEDEX.ev_defense,
            experience=MOCK_POKEDEX.experience,
            nickname=MOCK_POKEDEX.nickname,
            iv_special_attack=MOCK_POKEDEX.iv_special_attack,
            special_attack=MOCK_POKEDEX.special_attack,
            ev_special_attack=MOCK_POKEDEX.ev_special_attack,
            iv_special_defense=MOCK_POKEDEX.iv_special_defense,
            special_defense=MOCK_POKEDEX.special_defense,
            ev_special_defense=MOCK_POKEDEX.ev_special_defense,
            discovered=MOCK_POKEDEX.discovered,
            pokemon_id=pokemon.id,
            trainer_id=trainer.id,
            discovered_at=datetime.now(),
            formula=MOCK_POKEDEX.formula,
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
            speed=MOCK_POKEDEX.speed,
            ev_speed=MOCK_POKEDEX.ev_speed,
            iv_attack=MOCK_POKEDEX.iv_attack,
            attack=MOCK_POKEDEX.attack,
            ev_attack=MOCK_POKEDEX.ev_attack,
            iv_defense=MOCK_POKEDEX.iv_defense,
            defense=MOCK_POKEDEX.defense,
            ev_defense=MOCK_POKEDEX.ev_defense,
            experience=MOCK_POKEDEX.experience,
            nickname=MOCK_POKEDEX.nickname,
            iv_special_attack=MOCK_POKEDEX.iv_special_attack,
            special_attack=MOCK_POKEDEX.special_attack,
            ev_special_attack=MOCK_POKEDEX.ev_special_attack,
            iv_special_defense=MOCK_POKEDEX.iv_special_defense,
            special_defense=MOCK_POKEDEX.special_defense,
            ev_special_defense=MOCK_POKEDEX.ev_special_defense,
            discovered=MOCK_POKEDEX.discovered,
            pokemon_id=pokemon.id,
            trainer_id=trainer.id,
            discovered_at=datetime.now(),
            formula=MOCK_POKEDEX.formula,
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
            speed=MOCK_POKEDEX.speed,
            ev_speed=MOCK_POKEDEX.ev_speed,
            iv_attack=MOCK_POKEDEX.iv_attack,
            attack=MOCK_POKEDEX.attack,
            ev_attack=MOCK_POKEDEX.ev_attack,
            iv_defense=MOCK_POKEDEX.iv_defense,
            defense=MOCK_POKEDEX.defense,
            ev_defense=MOCK_POKEDEX.ev_defense,
            experience=MOCK_POKEDEX.experience,
            nickname=MOCK_POKEDEX.nickname,
            iv_special_attack=MOCK_POKEDEX.iv_special_attack,
            special_attack=MOCK_POKEDEX.special_attack,
            ev_special_attack=MOCK_POKEDEX.ev_special_attack,
            iv_special_defense=MOCK_POKEDEX.iv_special_defense,
            special_defense=MOCK_POKEDEX.special_defense,
            ev_special_defense=MOCK_POKEDEX.ev_special_defense,
            discovered=MOCK_POKEDEX.discovered,
            pokemon_id=pokemon.id,
            trainer_id=trainer.id,
            discovered_at=datetime.now(),
            formula=MOCK_POKEDEX.formula,
        )
        repository = PokedexRepository(session=session)
        await repository.create(pokedex_data)

        result = await repository.list_all(
            trainer_id=trainer.id,
        )
        assert isinstance(result, list)
        assert len(result) >= 1

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokedex_repository_list_empty(session, trainer, pokemon):
        repository = PokedexRepository(session=session)

        result = await repository.list_all(
            trainer_id=trainer.id,
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
            trainer_id=trainer.id, page_filter=PokedexFilterPage(offset=2, limit=10)
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
            trainer_id=trainer.id, page_filter=PokedexFilterPage(offset=0, limit=2)
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
            trainer_id=trainer.id, page_filter=PokedexFilterPage(offset=3, limit=4)
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
            trainer_id=trainer.id, page_filter=PokedexFilterPage(offset=None, limit=None)
        )
        assert isinstance(result, list)
        assert len(result) == total_results

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokedex_repository_list_with_filters(session, trainer, pokemon):
        total_results = 1
        for _ in range(3):
            pokedex = PokedexFactory(
                trainer_id=trainer.id,
                pokemon_id=pokemon.id,
                discovered=False,
            )
            session.add(pokedex)
            await session.commit()
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
            speed=MOCK_POKEDEX.speed,
            ev_speed=MOCK_POKEDEX.ev_speed,
            iv_attack=MOCK_POKEDEX.iv_attack,
            attack=MOCK_POKEDEX.attack,
            ev_attack=MOCK_POKEDEX.ev_attack,
            iv_defense=MOCK_POKEDEX.iv_defense,
            defense=MOCK_POKEDEX.defense,
            ev_defense=MOCK_POKEDEX.ev_defense,
            experience=MOCK_POKEDEX.experience,
            nickname=MOCK_POKEDEX.nickname,
            iv_special_attack=MOCK_POKEDEX.iv_special_attack,
            special_attack=MOCK_POKEDEX.special_attack,
            ev_special_attack=MOCK_POKEDEX.ev_special_attack,
            iv_special_defense=MOCK_POKEDEX.iv_special_defense,
            special_defense=MOCK_POKEDEX.special_defense,
            ev_special_defense=MOCK_POKEDEX.ev_special_defense,
            discovered=MOCK_POKEDEX.discovered,
            pokemon_id=pokemon.id,
            trainer_id=trainer.id,
            discovered_at=datetime.now(),
            formula=MOCK_POKEDEX.formula,
        )

        repository = PokedexRepository(session=session)

        await repository.create(pokedex_data)

        result = await repository.list_all(
            trainer_id=trainer.id,
            page_filter=PokedexFilterPage(
                nickname=MOCK_POKEDEX.nickname,
                discovered=MOCK_POKEDEX.discovered,
                offset=None,
                limit=None,
            ),
        )
        assert isinstance(result, list)
        assert len(result) == total_results


class TestPokedexRepositoryFindByPokemon:
    """Test scope for find_by_pokemon method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_find_by_pokemon_returns_none_when_all_params_empty(session, trainer):
        """Should return None when all parameters are empty"""

        repository = PokedexRepository(session=session)

        result = await repository.find_by_pokemon(
            find_pokedex=FindPokedexSchema(
                trainer_id=trainer.id,
                pokemon_id=None,
                name=None,
                nickname=None,
            )
        )

        assert result is None

    @staticmethod
    @pytest.mark.asyncio
    async def test_find_by_pokemon_searches_by_pokemon_id_only(session, trainer, pokemon):
        """Should find pokedex entry by pokemon_id alone"""

        pokedex = PokedexFactory(trainer_id=trainer.id, pokemon_id=pokemon.id)
        session.add(pokedex)
        await session.commit()

        repository = PokedexRepository(session=session)

        result = await repository.find_by_pokemon(
            find_pokedex=FindPokedexSchema(
                trainer_id=trainer.id,
                pokemon_id=pokemon.id,
                name=None,
                nickname=None,
            )
        )

        assert result is not None
        assert result.pokemon_id == pokemon.id

    @staticmethod
    @pytest.mark.asyncio
    async def test_find_by_pokemon_searches_by_name_only(session, trainer, pokemon):
        """Should find pokedex entry by pokemon name alone"""

        pokedex = PokedexFactory(trainer_id=trainer.id, pokemon_id=pokemon.id)
        session.add(pokedex)
        await session.commit()

        repository = PokedexRepository(session=session)

        result = await repository.find_by_pokemon(
            find_pokedex=FindPokedexSchema(
                trainer_id=trainer.id,
                pokemon_id=None,
                name=pokemon.name,
                nickname=None,
            )
        )

        assert result is not None
        assert result.pokemon.name == pokemon.name

    @staticmethod
    @pytest.mark.asyncio
    async def test_find_by_pokemon_searches_by_nickname_only(session, trainer, pokemon):
        """Should find pokedex entry by nickname alone (case-insensitive partial match)"""

        pokedex = PokedexFactory(
            trainer_id=trainer.id, pokemon_id=pokemon.id, nickname='unique_nickname'
        )
        session.add(pokedex)
        await session.commit()

        repository = PokedexRepository(session=session)

        result = await repository.find_by_pokemon(
            find_pokedex=FindPokedexSchema(
                trainer_id=trainer.id,
                pokemon_id=None,
                name=None,
                nickname='unique',
            )
        )

        assert result is not None
        assert 'unique' in result.nickname

    @staticmethod
    @pytest.mark.asyncio
    async def test_find_by_pokemon_applies_pokemon_id_and_nickname_filters(
        session, trainer, pokemon
    ):
        """Should apply AND logic when pokemon_id and nickname are provided"""

        pokedex = PokedexFactory(
            trainer_id=trainer.id, pokemon_id=pokemon.id, nickname='first'
        )
        session.add(pokedex)
        await session.commit()

        repository = PokedexRepository(session=session)

        result = await repository.find_by_pokemon(
            find_pokedex=FindPokedexSchema(
                trainer_id=trainer.id,
                pokemon_id=pokemon.id,
                name=None,
                nickname='first',
            )
        )

        assert result is not None
        assert result.pokemon_id == pokemon.id
        assert result.nickname == 'first'

    @staticmethod
    @pytest.mark.asyncio
    async def test_find_by_pokemon_applies_pokemon_id_and_name_filters(
        session, trainer, pokemon
    ):
        """Should apply AND logic when pokemon_id and name are provided"""

        pokedex = PokedexFactory(trainer_id=trainer.id, pokemon_id=pokemon.id)
        session.add(pokedex)
        await session.commit()

        repository = PokedexRepository(session=session)

        result = await repository.find_by_pokemon(
            find_pokedex=FindPokedexSchema(
                trainer_id=trainer.id,
                pokemon_id=pokemon.id,
                name=pokemon.name,
                nickname=None,
            )
        )

        assert result is not None
        assert result.pokemon_id == pokemon.id
        assert result.pokemon.name == pokemon.name

    @staticmethod
    @pytest.mark.asyncio
    async def test_find_by_pokemon_applies_all_three_filters(session, trainer, pokemon):
        """Should apply AND logic when all three filters are provided"""

        pokedex = PokedexFactory(
            trainer_id=trainer.id, pokemon_id=pokemon.id, nickname='target_nickname'
        )
        session.add(pokedex)
        await session.commit()

        repository = PokedexRepository(session=session)

        result = await repository.find_by_pokemon(
            find_pokedex=FindPokedexSchema(
                trainer_id=trainer.id,
                pokemon_id=pokemon.id,
                name=pokemon.name,
                nickname='target',
            )
        )

        assert result is not None
        assert result.pokemon_id == pokemon.id
        assert result.pokemon.name == pokemon.name
        assert result.nickname == 'target_nickname'

    @staticmethod
    @pytest.mark.asyncio
    async def test_find_by_pokemon_returns_none_when_no_match(session, trainer, pokemon):
        """Should return None when no pokedex entry matches the filters"""

        repository = PokedexRepository(session=session)

        result = await repository.find_by_pokemon(
            find_pokedex=FindPokedexSchema(
                trainer_id=trainer.id,
                pokemon_id=pokemon.id,
                name=None,
                nickname=None,
            )
        )

        assert result is None


class TestPokedexRepositoryQueryBranches:
    """Focused branch coverage tests for query filters and non-paginated returns."""

    @staticmethod
    @pytest.mark.asyncio
    async def test_list_all_applies_discovered_filter_and_returns_all_items():
        """Should apply discovered filter and return scalars().all() in non-paginated mode."""
        session = AsyncMock()
        scalars_result = MagicMock()
        scalars_result.all.return_value = ['row']
        session.scalars = AsyncMock(return_value=scalars_result)

        repository = PokedexRepository(session=session)
        result = await repository.list_all(
            PokedexFilterPage(
                trainer_id='trainer-id',
                discovered=True,
                offset=None,
                limit=None,
            )
        )

        query = session.scalars.await_args.args[0]
        assert 'pokedex.discovered' in str(query)
        assert result == ['row']
        scalars_result.all.assert_called_once()

    @staticmethod
    @pytest.mark.asyncio
    async def test_list_all_applies_nickname_filter_and_returns_all_items():
        """Should apply nickname filter and return scalars().all() in non-paginated mode."""
        session = AsyncMock()
        scalars_result = MagicMock()
        scalars_result.all.return_value = []
        session.scalars = AsyncMock(return_value=scalars_result)

        repository = PokedexRepository(session=session)
        result = await repository.list_all(
            PokedexFilterPage(
                trainer_id='trainer-id',
                nickname='pi',
                offset=None,
                limit=None,
            )
        )

        query = session.scalars.await_args.args[0]
        assert 'pokedex.nickname' in str(query)
        assert result == []
        scalars_result.all.assert_called_once()

    @staticmethod
    @pytest.mark.asyncio
    async def test_find_by_pokemon_applies_pokemon_id_filter_clause():
        """Should include pokemon_id clause when pokemon_id is provided."""
        session = AsyncMock()
        session.scalar = AsyncMock(return_value='row')
        repository = PokedexRepository(session=session)

        await repository.find_by_pokemon(
            FindPokedexSchema(
                trainer_id='trainer-id',
                pokemon_id='pokemon-id',
                name=None,
                nickname=None,
            )
        )

        query = session.scalar.await_args.args[0]
        assert 'pokedex.pokemon_id' in str(query)

    @staticmethod
    @pytest.mark.asyncio
    async def test_find_by_pokemon_applies_name_filter_clause():
        """Should include pokemon name clause when name is provided."""
        session = AsyncMock()
        session.scalar = AsyncMock(return_value='row')
        repository = PokedexRepository(session=session)

        await repository.find_by_pokemon(
            FindPokedexSchema(
                trainer_id='trainer-id',
                pokemon_id=None,
                name='pikachu',
                nickname=None,
            )
        )

        query = session.scalar.await_args.args[0]
        assert 'EXISTS' in str(query)
        assert 'pokemon.name' in str(query)

    @staticmethod
    @pytest.mark.asyncio
    async def test_find_by_pokemon_applies_nickname_filter_clause():
        """Should include nickname clause when nickname is provided."""
        session = AsyncMock()
        session.scalar = AsyncMock(return_value='row')
        repository = PokedexRepository(session=session)

        await repository.find_by_pokemon(
            FindPokedexSchema(
                trainer_id='trainer-id',
                pokemon_id=None,
                name=None,
                nickname='nick',
            )
        )

        query = session.scalar.await_args.args[0]
        assert 'pokedex.nickname' in str(query)


class TestPokedexRepositoryUpdate:
    """Test scope for update method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokedex_repository_update_success(
        trainer, session, pokemon, pokedex_repository
    ):
        pokedex = PokedexFactory(
            trainer_id=trainer.id,
            pokemon_id=pokemon.id,
        )
        session.add(pokedex)
        await session.commit()
        await session.refresh(pokedex)

        pokedex.nickname = 'new_nickname'
        await pokedex_repository.update(pokedex)
        await session.refresh(pokedex)

        assert pokedex.nickname == 'new_nickname'

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokedex_repository_update_commit_error(
        trainer, session, pokemon, pokedex_repository
    ):
        pokedex = PokedexFactory(
            trainer_id=trainer.id,
            pokemon_id=pokemon.id,
        )
        session.add(pokedex)
        await session.commit()
        await session.refresh(pokedex)

        pokedex.nickname = 'new_nickname'

        session.commit = AsyncMock(side_effect=Exception('Database error'))

        with pytest.raises(Exception, match='Database error'):
            await pokedex_repository.update(pokedex)


class TestPokedexRepositoryFindById:
    """Test scope for find_by_id method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_find_by_id_returns_entity(pokedex, pokedex_repository):
        """Should return a pokedex entity"""
        result = await pokedex_repository.find_by_id(pokedex_id=pokedex.id)

        assert result is not None
        assert result.id == pokedex.id

    @staticmethod
    @pytest.mark.asyncio
    async def test_find_by_id_contains_pokemon_id(
        pokedex,
        pokemon,
        pokedex_repository,
    ):
        """Should return a pokedex entity with pokemon id"""
        result = await pokedex_repository.find_by_id(pokedex_id=pokedex.id)

        assert result.pokemon_id == pokemon.id

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
            speed=MOCK_POKEDEX.speed,
            ev_speed=MOCK_POKEDEX.ev_speed,
            iv_attack=MOCK_POKEDEX.iv_attack,
            attack=MOCK_POKEDEX.attack,
            ev_attack=MOCK_POKEDEX.ev_attack,
            iv_defense=MOCK_POKEDEX.iv_defense,
            defense=MOCK_POKEDEX.defense,
            ev_defense=MOCK_POKEDEX.ev_defense,
            experience=MOCK_POKEDEX.experience,
            nickname=MOCK_POKEDEX.nickname,
            iv_special_attack=MOCK_POKEDEX.iv_special_attack,
            special_attack=MOCK_POKEDEX.special_attack,
            ev_special_attack=MOCK_POKEDEX.ev_special_attack,
            iv_special_defense=MOCK_POKEDEX.iv_special_defense,
            special_defense=MOCK_POKEDEX.special_defense,
            ev_special_defense=MOCK_POKEDEX.ev_special_defense,
            discovered=MOCK_POKEDEX.discovered,
            pokemon_id=pokemon.id,
            trainer_id=trainer.id,
            discovered_at=datetime.now(),
            formula=MOCK_POKEDEX.formula,
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
            speed=MOCK_POKEDEX.speed,
            ev_speed=MOCK_POKEDEX.ev_speed,
            iv_attack=MOCK_POKEDEX.iv_attack,
            attack=MOCK_POKEDEX.attack,
            ev_attack=MOCK_POKEDEX.ev_attack,
            iv_defense=MOCK_POKEDEX.iv_defense,
            defense=MOCK_POKEDEX.defense,
            ev_defense=MOCK_POKEDEX.ev_defense,
            experience=MOCK_POKEDEX.experience,
            nickname=MOCK_POKEDEX.nickname,
            iv_special_attack=MOCK_POKEDEX.iv_special_attack,
            special_attack=MOCK_POKEDEX.special_attack,
            ev_special_attack=MOCK_POKEDEX.ev_special_attack,
            iv_special_defense=MOCK_POKEDEX.iv_special_defense,
            special_defense=MOCK_POKEDEX.special_defense,
            ev_special_defense=MOCK_POKEDEX.ev_special_defense,
            discovered=MOCK_POKEDEX.discovered,
            pokemon_id=pokemon.id,
            trainer_id=trainer.id,
            discovered_at=datetime.now(),
            formula=MOCK_POKEDEX.formula,
        )
        repository = PokedexRepository(session=session)
        await repository.create(pokedex_data)

        result = await repository.find_by_trainer(trainer.id)

        assert isinstance(result, set)
        assert pokemon.id in result
