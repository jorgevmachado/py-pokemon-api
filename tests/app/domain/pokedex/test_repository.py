from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from app.models.pokedex import Pokedex
from app.shared.schemas import FilterPage
from tests.factories.pokedex import MOCK_POKEDEX, PokedexFactory


def _build_pokedex_entity(trainer_id: str, pokemon_id: str, nickname: str, discovered: bool):
    entity = Pokedex(
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
        nickname=nickname,
        iv_special_attack=MOCK_POKEDEX.iv_special_attack,
        special_attack=MOCK_POKEDEX.special_attack,
        ev_special_attack=MOCK_POKEDEX.ev_special_attack,
        iv_special_defense=MOCK_POKEDEX.iv_special_defense,
        special_defense=MOCK_POKEDEX.special_defense,
        ev_special_defense=MOCK_POKEDEX.ev_special_defense,
        discovered=discovered,
        pokemon_id=pokemon_id,
        trainer_id=trainer_id,
        formula=MOCK_POKEDEX.formula,
    )
    entity.discovered_at = datetime.now()
    return entity


class TestPokedexRepositorySave:
    """Test scope for save method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokedex_repository_save_success(trainer, pokemon, pokedex_repository):
        """Should persist pokedex when data is valid"""
        entity = _build_pokedex_entity(
            trainer_id=trainer.id,
            pokemon_id=pokemon.id,
            nickname=MOCK_POKEDEX.nickname,
            discovered=MOCK_POKEDEX.discovered,
        )

        result = await pokedex_repository.save(entity=entity)

        assert result.id is not None
        assert result.trainer_id == trainer.id
        assert result.pokemon_id == pokemon.id
        assert result.nickname == MOCK_POKEDEX.nickname

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokedex_repository_save_commit_error(
        session,
        trainer,
        pokemon,
        pokedex_repository,
    ):
        """Should raise exception when database commit fails"""
        session.commit = AsyncMock(side_effect=Exception('Database error'))
        entity = _build_pokedex_entity(
            trainer_id=trainer.id,
            pokemon_id=pokemon.id,
            nickname=MOCK_POKEDEX.nickname,
            discovered=MOCK_POKEDEX.discovered,
        )

        with pytest.raises(Exception, match='Database error'):
            await pokedex_repository.save(entity=entity)


class TestPokedexRepositoryFindBy:
    """Test scope for find_by method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_find_by_trainer_returns_entry(trainer, pokedex, pokedex_repository):
        """Should return first trainer pokedex entry"""

        result = await pokedex_repository.find_by(trainer_id=trainer.id)

        assert result is not None
        assert result.trainer_id == trainer.id

    @staticmethod
    @pytest.mark.asyncio
    async def test_find_by_trainer_returns_none_for_nonexistent_trainer(pokedex_repository):
        """Should return None for nonexistent trainer"""
        nonexistent_trainer_id = '00000000-0000-0000-0000-000000000000'

        result = await pokedex_repository.find_by(trainer_id=nonexistent_trainer_id)

        assert result is None

    @staticmethod
    @pytest.mark.asyncio
    async def test_find_by_returns_none_when_no_valid_filters(pokedex_repository):
        """Should return None when all filters are invalid"""
        result = await pokedex_repository.find_by(pokemon_id=None, trainer_id=None, id=None)

        assert result is None

    @staticmethod
    @pytest.mark.asyncio
    async def test_find_by_pokemon_searches_by_pokemon_id_only(
        pokedex, pokedex_repository, trainer, pokemon
    ):
        """Should find pokedex entry by pokemon_id alone"""
        result = await pokedex_repository.find_by(
            trainer_id=trainer.id,
            pokemon_id=pokemon.id,
            pokemon_name=None,
            nickname=None,
        )

        assert result is not None
        assert result.pokemon_id == pokemon.id

    @staticmethod
    @pytest.mark.asyncio
    async def test_find_by_pokemon_searches_by_name_only(
        session, trainer, pokemon, pokemon_incomplete, pokedex_repository
    ):
        """Should find pokedex entry by pokemon name alone"""

        entry_a = PokedexFactory(trainer_id=trainer.id, pokemon_id=pokemon.id, nickname='a')
        entry_b = PokedexFactory(
            trainer_id=trainer.id,
            pokemon_id=pokemon_incomplete.id,
            nickname='b',
        )
        session.add(entry_a)
        await session.commit()
        session.add(entry_b)
        await session.commit()

        result = await pokedex_repository.find_by(
            trainer_id=trainer.id,
            pokemon_name=pokemon.name,
        )

        assert result is not None
        assert result.pokemon.name == pokemon.name

    @staticmethod
    @pytest.mark.asyncio
    async def test_find_by_pokemon_searches_by_nickname_only(
        session, trainer, pokemon, pokedex_repository
    ):
        """Should find pokedex entry by nickname alone (case-insensitive partial match)"""

        pokedex = PokedexFactory(
            trainer_id=trainer.id, pokemon_id=pokemon.id, nickname='unique'
        )
        session.add(pokedex)
        await session.commit()

        result = await pokedex_repository.find_by(
            trainer_id=trainer.id,
            pokemon_id=None,
            pokemon_name=None,
            nickname='unique',
        )

        assert result is not None
        assert 'unique' in result.nickname

    @staticmethod
    @pytest.mark.asyncio
    async def test_find_by_pokemon_applies_pokemon_id_and_nickname_filters(
        session, trainer, pokemon, pokedex_repository
    ):
        """Should apply AND logic when pokemon_id and nickname are provided"""

        pokedex = PokedexFactory(
            trainer_id=trainer.id, pokemon_id=pokemon.id, nickname='first'
        )
        session.add(pokedex)
        await session.commit()

        result = await pokedex_repository.find_by(
            trainer_id=trainer.id,
            pokemon_id=pokemon.id,
            nickname='first',
        )

        assert result is not None
        assert result.pokemon_id == pokemon.id
        assert result.nickname == 'first'

    @staticmethod
    @pytest.mark.asyncio
    async def test_find_by_pokemon_applies_pokemon_id_and_name_filters(
        session, trainer, pokemon, pokedex_repository
    ):
        """Should apply AND logic when pokemon_id and name are provided"""

        pokedex = PokedexFactory(trainer_id=trainer.id, pokemon_id=pokemon.id)
        session.add(pokedex)
        await session.commit()

        result = await pokedex_repository.find_by(
            trainer_id=trainer.id,
            pokemon_id=pokemon.id,
            pokemon_name=pokemon.name,
            nickname=None,
        )

        assert result is not None
        assert result.pokemon_id == pokemon.id
        assert result.pokemon.name == pokemon.name

    @staticmethod
    @pytest.mark.asyncio
    async def test_find_by_pokemon_applies_all_three_filters(
        session, trainer, pokemon, pokedex_repository
    ):
        """Should apply AND logic when all three filters are provided"""

        pokedex = PokedexFactory(
            trainer_id=trainer.id, pokemon_id=pokemon.id, nickname='target_nickname'
        )
        session.add(pokedex)
        await session.commit()

        result = await pokedex_repository.find_by(
            trainer_id=trainer.id,
            pokemon_id=pokemon.id,
            pokemon_name=pokemon.name,
            nickname='target_nickname',
        )

        assert result is not None
        assert result.pokemon_id == pokemon.id
        assert result.pokemon.name == pokemon.name
        assert result.nickname == 'target_nickname'

    @staticmethod
    @pytest.mark.asyncio
    async def test_find_by_pokemon_returns_none_when_no_match(
        trainer, pokemon, pokedex_repository
    ):
        """Should return None when no pokedex entry matches the filters"""
        result = await pokedex_repository.find_by(
            trainer_id=trainer.id,
            pokemon_id=pokemon.id,
            nickname='does-not-exist',
        )

        assert result is None

    @staticmethod
    @pytest.mark.asyncio
    async def test_find_by_id_returns_entity(pokedex, pokedex_repository):
        """Should return a pokedex entity"""
        result = await pokedex_repository.find_by(id=pokedex.id)

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
        result = await pokedex_repository.find_by(id=pokedex.id)

        assert result.pokemon_id == pokemon.id

    @staticmethod
    @pytest.mark.asyncio
    async def test_find_by_id_returns_none_for_nonexistent_id(pokedex_repository):
        """Should return None for nonexistent pokedex id"""
        nonexistent_pokedex_id = '00000000-0000-0000-0000-000000000000'

        result = await pokedex_repository.find_by(id=nonexistent_pokedex_id)

        assert result is None


class TestPokedexRepositoryList:
    """Test scope for list_by_trainer method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokedex_repository_list_success(
        pokedex, session, trainer, pokemon, pokedex_repository
    ):

        result = await pokedex_repository.list_all(
            page_filter=FilterPage.build(trainer_id=trainer.id)
        )
        assert isinstance(result, list)
        assert len(result) >= 1

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokedex_repository_list_empty(pokedex_repository, trainer, pokemon):
        result = await pokedex_repository.list_all(
            page_filter=FilterPage.build(trainer_id=trainer.id)
        )
        assert isinstance(result, list)
        assert len(result) == 0

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokedex_repository_list_with_offset(
        session,
        trainer,
        pokemon,
        pokedex_repository,
    ):
        for _ in range(5):
            pokedex = PokedexFactory(trainer_id=trainer.id, pokemon_id=pokemon.id)
            session.add(pokedex)
            await session.commit()

        result = await pokedex_repository.list_all(
            page_filter=FilterPage.build(trainer_id=trainer.id, offset=2, limit=10),
        )
        assert result is not None
        assert hasattr(result, 'items')
        assert len(result.items) >= 1

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokedex_repository_list_with_limit(
        session,
        trainer,
        pokemon,
        pokedex_repository,
    ):
        total_results = 2
        for _ in range(5):
            pokedex = PokedexFactory(trainer_id=trainer.id, pokemon_id=pokemon.id)
            session.add(pokedex)
            await session.commit()

        result = await pokedex_repository.list_all(
            page_filter=FilterPage.build(trainer_id=trainer.id, offset=0, limit=2)
        )
        assert result is not None
        if hasattr(result, 'items'):
            assert len(result.items) == total_results
        else:
            assert len(result) == total_results

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokedex_repository_list_with_offset_and_limit(
        session, trainer, pokemon, pokedex_repository
    ):
        total_results = 4
        for _ in range(10):
            pokedex = PokedexFactory(trainer_id=trainer.id, pokemon_id=pokemon.id)
            session.add(pokedex)
            await session.commit()

        result = await pokedex_repository.list_all(
            page_filter=FilterPage.build(trainer_id=trainer.id, offset=3, limit=4)
        )
        assert result is not None
        if hasattr(result, 'items'):
            assert len(result.items) == total_results
        else:
            assert len(result) == total_results

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokedex_repository_list_without_pagination(
        session, trainer, pokemon, pokedex_repository
    ):
        total_results = 3
        for _ in range(3):
            pokedex = PokedexFactory(trainer_id=trainer.id, pokemon_id=pokemon.id)
            session.add(pokedex)
            await session.commit()

        result = await pokedex_repository.list_all(
            page_filter=FilterPage.build(trainer_id=trainer.id, offset=None, limit=None)
        )
        assert isinstance(result, list)
        assert len(result) == total_results

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokedex_repository_list_with_filters(
        session, trainer, pokemon, pokedex_repository
    ):
        total_results = 1
        for _ in range(3):
            pokedex = PokedexFactory(
                trainer_id=trainer.id,
                pokemon_id=pokemon.id,
                discovered=False,
            )
            session.add(pokedex)
            await session.commit()

        filtered_pokedex = PokedexFactory(
            trainer_id=trainer.id,
            pokemon_id=pokemon.id,
            nickname=MOCK_POKEDEX.nickname,
            discovered=MOCK_POKEDEX.discovered,
        )
        session.add(filtered_pokedex)
        await session.commit()

        result = await pokedex_repository.list_all(
            page_filter=FilterPage.build(
                trainer_id=trainer.id,
                nickname=MOCK_POKEDEX.nickname,
                discovered=MOCK_POKEDEX.discovered,
                offset=None,
                limit=None,
            ),
        )
        assert isinstance(result, list)
        assert len(result) == total_results

    @staticmethod
    @pytest.mark.asyncio
    async def test_pokedex_repository_list_with_pokemon_type_filter(
        session, trainer, pokemon, pokemon_type, pokedex_repository
    ):
        pokemon.types.append(pokemon_type)
        session.add(pokemon)
        await session.commit()
        await session.refresh(pokemon)

        entry = PokedexFactory(trainer_id=trainer.id, pokemon_id=pokemon.id)
        session.add(entry)
        await session.commit()

        result = await pokedex_repository.list_all(
            page_filter=FilterPage.build(
                trainer_id=trainer.id,
                pokemon_type='fire',
                offset=None,
                limit=None,
            )
        )

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].pokemon.id == pokemon.id


class TestPokedexRepositoryQueryBranches:
    """Query-specific branch tests removed as they duplicated behavior assertions."""


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
