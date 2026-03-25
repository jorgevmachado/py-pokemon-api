from unittest.mock import AsyncMock

import pytest

from app.models.captured_pokemon import CapturedPokemon
from app.shared.schemas import FilterPage
from tests.factories.captured_pokemon import MOCK_CAPTURED_POKEMON, CapturedPokemonFactory


class TestCapturedPokemonRepositorySave:
    """Test scope for create method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_captured_pokemon_repository_save_success(
        captured_pokemon_repository, trainer, pokemon
    ):
        """Should persist captured pokemon when data is valid"""
        result = await captured_pokemon_repository.save(
            entity=CapturedPokemon(
                hp=MOCK_CAPTURED_POKEMON.hp,
                wins=MOCK_CAPTURED_POKEMON.wins,
                level=MOCK_CAPTURED_POKEMON.level,
                iv_hp=MOCK_CAPTURED_POKEMON.iv_hp,
                ev_hp=MOCK_CAPTURED_POKEMON.ev_hp,
                losses=MOCK_CAPTURED_POKEMON.losses,
                max_hp=MOCK_CAPTURED_POKEMON.max_hp,
                battles=MOCK_CAPTURED_POKEMON.battles,
                iv_speed=MOCK_CAPTURED_POKEMON.iv_speed,
                speed=MOCK_CAPTURED_POKEMON.speed,
                ev_speed=MOCK_CAPTURED_POKEMON.ev_speed,
                iv_attack=MOCK_CAPTURED_POKEMON.iv_attack,
                attack=MOCK_CAPTURED_POKEMON.attack,
                ev_attack=MOCK_CAPTURED_POKEMON.ev_attack,
                iv_defense=MOCK_CAPTURED_POKEMON.iv_defense,
                defense=MOCK_CAPTURED_POKEMON.defense,
                ev_defense=MOCK_CAPTURED_POKEMON.ev_defense,
                experience=MOCK_CAPTURED_POKEMON.experience,
                nickname=MOCK_CAPTURED_POKEMON.nickname,
                iv_special_attack=MOCK_CAPTURED_POKEMON.iv_special_attack,
                special_attack=MOCK_CAPTURED_POKEMON.special_attack,
                ev_special_attack=MOCK_CAPTURED_POKEMON.ev_special_attack,
                iv_special_defense=MOCK_CAPTURED_POKEMON.iv_special_defense,
                special_defense=MOCK_CAPTURED_POKEMON.special_defense,
                ev_special_defense=MOCK_CAPTURED_POKEMON.ev_special_defense,
                captured_at=MOCK_CAPTURED_POKEMON.captured_at,
                pokemon_id=pokemon.id,
                trainer_id=trainer.id,
                formula=MOCK_CAPTURED_POKEMON.formula,
            )
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
    async def test_captured_pokemon_repository_save_commit_error(
        captured_pokemon_repository, session, trainer, pokemon
    ):
        """Should raise exception when database commit fails"""
        session.commit = AsyncMock(side_effect=Exception('Database error'))

        with pytest.raises(Exception, match='Database error'):
            await captured_pokemon_repository.save(
                entity=CapturedPokemon(
                    hp=MOCK_CAPTURED_POKEMON.hp,
                    wins=MOCK_CAPTURED_POKEMON.wins,
                    level=MOCK_CAPTURED_POKEMON.level,
                    iv_hp=MOCK_CAPTURED_POKEMON.iv_hp,
                    ev_hp=MOCK_CAPTURED_POKEMON.ev_hp,
                    losses=MOCK_CAPTURED_POKEMON.losses,
                    max_hp=MOCK_CAPTURED_POKEMON.max_hp,
                    battles=MOCK_CAPTURED_POKEMON.battles,
                    iv_speed=MOCK_CAPTURED_POKEMON.iv_speed,
                    speed=MOCK_CAPTURED_POKEMON.speed,
                    ev_speed=MOCK_CAPTURED_POKEMON.ev_speed,
                    iv_attack=MOCK_CAPTURED_POKEMON.iv_attack,
                    attack=MOCK_CAPTURED_POKEMON.attack,
                    ev_attack=MOCK_CAPTURED_POKEMON.ev_attack,
                    iv_defense=MOCK_CAPTURED_POKEMON.iv_defense,
                    defense=MOCK_CAPTURED_POKEMON.defense,
                    ev_defense=MOCK_CAPTURED_POKEMON.ev_defense,
                    experience=MOCK_CAPTURED_POKEMON.experience,
                    nickname=MOCK_CAPTURED_POKEMON.nickname,
                    iv_special_attack=MOCK_CAPTURED_POKEMON.iv_special_attack,
                    special_attack=MOCK_CAPTURED_POKEMON.special_attack,
                    ev_special_attack=MOCK_CAPTURED_POKEMON.ev_special_attack,
                    iv_special_defense=MOCK_CAPTURED_POKEMON.iv_special_defense,
                    special_defense=MOCK_CAPTURED_POKEMON.special_defense,
                    ev_special_defense=MOCK_CAPTURED_POKEMON.ev_special_defense,
                    captured_at=MOCK_CAPTURED_POKEMON.captured_at,
                    pokemon_id=pokemon.id,
                    trainer_id=trainer.id,
                    formula=MOCK_CAPTURED_POKEMON.formula,
                )
            )


class TestCapturedPokemonRepositoryListByTrainer:
    """Test scope for list_by_trainer method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_captured_pokemon_repository_list_success(
        trainer, captured_pokemon, captured_pokemon_repository
    ):
        result = await captured_pokemon_repository.list_all(
            page_filter=FilterPage(trainer_id=trainer.id)
        )
        assert isinstance(result, list)
        assert len(result) >= 1

    @staticmethod
    @pytest.mark.asyncio
    async def test_captured_pokemon_repository_list_empty(
        trainer, pokemon, captured_pokemon_repository
    ):

        result = await captured_pokemon_repository.list_all(
            page_filter=FilterPage(trainer_id=trainer.id)
        )
        assert isinstance(result, list)
        assert len(result) == 0

    @staticmethod
    @pytest.mark.asyncio
    async def test_captured_pokemon_repository_list_with_offset(
        session, trainer, pokemon, captured_pokemon_repository
    ):
        for _ in range(5):
            pokedex = CapturedPokemonFactory(trainer_id=trainer.id, pokemon_id=pokemon.id)
            session.add(pokedex)
            await session.commit()

        result = await captured_pokemon_repository.list_all(
            page_filter=FilterPage(
                offset=2,
                limit=10,
                trainer_id=trainer.id,
            )
        )
        assert result is not None
        assert hasattr(result, 'items')
        assert len(result.items) >= 1

    @staticmethod
    @pytest.mark.asyncio
    async def test_captured_pokemon_repository_list_with_limit(
        session, trainer, pokemon, captured_pokemon_repository
    ):
        total_results = 2
        for _ in range(5):
            pokedex = CapturedPokemonFactory(trainer_id=trainer.id, pokemon_id=pokemon.id)
            session.add(pokedex)
            await session.commit()

        result = await captured_pokemon_repository.list_all(
            page_filter=FilterPage(offset=0, limit=2, trainer_id=trainer.id)
        )
        assert result is not None
        if hasattr(result, 'items'):
            assert len(result.items) == total_results
        else:
            assert len(result) == total_results

    @staticmethod
    @pytest.mark.asyncio
    async def test_captured_pokemon_repository_list_with_offset_and_limit(
        session, trainer, pokemon, captured_pokemon_repository
    ):
        total_results = 4
        for _ in range(10):
            pokedex = CapturedPokemonFactory(trainer_id=trainer.id, pokemon_id=pokemon.id)
            session.add(pokedex)
            await session.commit()

        result = await captured_pokemon_repository.list_all(
            page_filter=FilterPage(offset=3, limit=4, trainer_id=trainer.id)
        )
        assert result is not None
        if hasattr(result, 'items'):
            assert len(result.items) == total_results
        else:
            assert len(result) == total_results

    @staticmethod
    @pytest.mark.asyncio
    async def test_captured_pokemon_repository_list_without_pagination(
        session, trainer, pokemon, captured_pokemon_repository
    ):
        total_results = 3
        for _ in range(3):
            pokedex = CapturedPokemonFactory(trainer_id=trainer.id, pokemon_id=pokemon.id)
            session.add(pokedex)
            await session.commit()

        result = await captured_pokemon_repository.list_all(
            page_filter=FilterPage(
                offset=None,
                limit=None,
                trainer_id=trainer.id,
            ),
        )
        assert isinstance(result, list)
        assert len(result) == total_results

    @staticmethod
    @pytest.mark.asyncio
    async def test_captured_pokemon_repository_list_with_filters(
        session, trainer, pokemon, captured_pokemon_repository
    ):
        total_results = 1
        for _ in range(3):
            captured_pokemon = CapturedPokemonFactory(
                trainer_id=trainer.id,
                pokemon_id=pokemon.id,
            )
            session.add(captured_pokemon)
            await session.commit()

        await captured_pokemon_repository.save(
            entity=CapturedPokemon(
                hp=MOCK_CAPTURED_POKEMON.hp,
                wins=MOCK_CAPTURED_POKEMON.wins,
                level=MOCK_CAPTURED_POKEMON.level,
                iv_hp=MOCK_CAPTURED_POKEMON.iv_hp,
                ev_hp=MOCK_CAPTURED_POKEMON.ev_hp,
                losses=MOCK_CAPTURED_POKEMON.losses,
                max_hp=MOCK_CAPTURED_POKEMON.max_hp,
                battles=MOCK_CAPTURED_POKEMON.battles,
                iv_speed=MOCK_CAPTURED_POKEMON.iv_speed,
                speed=MOCK_CAPTURED_POKEMON.speed,
                ev_speed=MOCK_CAPTURED_POKEMON.ev_speed,
                iv_attack=MOCK_CAPTURED_POKEMON.iv_attack,
                attack=MOCK_CAPTURED_POKEMON.attack,
                ev_attack=MOCK_CAPTURED_POKEMON.ev_attack,
                iv_defense=MOCK_CAPTURED_POKEMON.iv_defense,
                defense=MOCK_CAPTURED_POKEMON.defense,
                ev_defense=MOCK_CAPTURED_POKEMON.ev_defense,
                experience=MOCK_CAPTURED_POKEMON.experience,
                nickname=MOCK_CAPTURED_POKEMON.nickname,
                iv_special_attack=MOCK_CAPTURED_POKEMON.iv_special_attack,
                special_attack=MOCK_CAPTURED_POKEMON.special_attack,
                ev_special_attack=MOCK_CAPTURED_POKEMON.ev_special_attack,
                iv_special_defense=MOCK_CAPTURED_POKEMON.iv_special_defense,
                special_defense=MOCK_CAPTURED_POKEMON.special_defense,
                ev_special_defense=MOCK_CAPTURED_POKEMON.ev_special_defense,
                captured_at=MOCK_CAPTURED_POKEMON.captured_at,
                pokemon_id=pokemon.id,
                trainer_id=trainer.id,
                formula=MOCK_CAPTURED_POKEMON.formula,
            )
        )

        result = await captured_pokemon_repository.list_all(
            page_filter=FilterPage.build(
                trainer_id=trainer.id,
                nickname=MOCK_CAPTURED_POKEMON.nickname,
                offset=None,
                limit=None,
            ),
        )
        assert isinstance(result, list)
        assert len(result) == total_results


class TestCapturedPokemonRepositoryFindBy:
    """Test scope for find_by method"""

    @staticmethod
    @pytest.mark.asyncio
    async def test_find_by_returns_none_when_all_params_empty(
        captured_pokemon_repository,
        trainer,
    ):
        """Should return None when pokemon_id, name and nickname are all None"""
        result = await captured_pokemon_repository.find_by(
            trainer_id=trainer.id,
        )

        assert result is None

    @staticmethod
    @pytest.mark.asyncio
    async def test_find_by_searches_by_pokemon_id_only(
        session,
        captured_pokemon_repository,
        captured_pokemon_service,
        trainer,
        pokemon,
    ):
        """Should find pokemon by pokemon_id alone"""
        await captured_pokemon_service.create(
            pokemon=pokemon, trainer=trainer, nickname='test'
        )

        result = await captured_pokemon_repository.find_by(
            trainer_id=trainer.id,
            pokemon_id=pokemon.id,
            name=None,
            nickname=None,
        )

        assert result is not None
        assert result.pokemon_id == pokemon.id

    @staticmethod
    @pytest.mark.asyncio
    async def test_find_by_searches_by_name_only(
        session,
        captured_pokemon_repository,
        captured_pokemon_service,
        trainer,
        pokemon,
    ):
        """Should find pokemon by name alone"""
        await captured_pokemon_service.create(
            pokemon=pokemon, trainer=trainer, nickname='test'
        )

        result = await captured_pokemon_repository.find_by(
            trainer_id=trainer.id,
            pokemon_id=None,
            name=pokemon.name,
            nickname=None,
        )

        assert result is not None
        assert result.pokemon.name == pokemon.name

    @staticmethod
    @pytest.mark.asyncio
    async def test_find_by_searches_by_nickname_only(
        session,
        captured_pokemon_repository,
        captured_pokemon_service,
        trainer,
        pokemon,
    ):
        """Should find pokemon by nickname alone (case-insensitive partial match)"""
        await captured_pokemon_service.create(
            pokemon=pokemon, trainer=trainer, nickname='unique_nickname'
        )

        result = await captured_pokemon_repository.find_by(
            trainer_id=trainer.id,
            pokemon_id=None,
            name=None,
            nickname='unique_nickname',
        )

        assert result is not None
        assert 'unique_nickname' in result.nickname

    @staticmethod
    @pytest.mark.asyncio
    async def test_find_by_applies_pokemon_id_and_nickname_filters(
        session,
        captured_pokemon_service,
        trainer,
        pokemon,
        pokemon_incomplete,
    ):
        """Should apply AND logic when pokemon_id and nickname are provided"""
        captured_1 = await captured_pokemon_service.create(
            pokemon=pokemon, trainer=trainer, nickname='first'
        )
        await captured_pokemon_service.create(
            pokemon=pokemon, trainer=trainer, nickname='second'
        )

        result = await captured_pokemon_service.repository.find_by(
            trainer_id=trainer.id,
            pokemon_id=pokemon.id,
            name=None,
            nickname='first',
        )

        assert result is not None
        assert result.id == captured_1.id
        assert result.pokemon_id == pokemon.id
        assert result.nickname == 'first'

    @staticmethod
    @pytest.mark.asyncio
    async def test_find_by_applies_pokemon_id_and_name_filters(
        session,
        captured_pokemon_service,
        trainer,
        pokemon,
        pokemon_incomplete,
    ):
        """Should apply AND logic when pokemon_id and name are provided"""
        await captured_pokemon_service.create(
            pokemon=pokemon, trainer=trainer, nickname='first'
        )
        await captured_pokemon_service.create(
            pokemon=pokemon_incomplete, trainer=trainer, nickname='second'
        )

        result = await captured_pokemon_service.repository.find_by(
            trainer_id=trainer.id,
            pokemon_id=pokemon.id,
            name=pokemon.name,
            nickname=None,
        )

        assert result is not None
        assert result.pokemon_id == pokemon.id
        assert result.pokemon.name == pokemon.name

    @staticmethod
    @pytest.mark.asyncio
    async def test_find_by_applies_all_three_filters(
        session,
        captured_pokemon_repository,
        captured_pokemon_service,
        trainer,
        pokemon,
    ):
        """Should apply AND logic when all three filters are provided"""
        await captured_pokemon_service.create(
            pokemon=pokemon, trainer=trainer, nickname='target_nickname'
        )

        result = await captured_pokemon_repository.find_by(
            trainer_id=trainer.id,
            pokemon_id=pokemon.id,
            name=pokemon.name,
            nickname='target_nickname',
        )

        assert result is not None
        assert result.pokemon_id == pokemon.id
        assert result.pokemon.name == pokemon.name
        assert result.nickname == 'target_nickname'

    @staticmethod
    @pytest.mark.asyncio
    async def test_find_by_returns_none_when_no_match(
        captured_pokemon_repository,
        trainer,
        pokemon,
    ):
        """Should return None when no pokemon matches the filters"""
        result = await captured_pokemon_repository.find_by(
            trainer_id=trainer.id,
            pokemon_id=pokemon.id,
            name=None,
            nickname=None,
        )

        assert result is None

    @staticmethod
    @pytest.mark.asyncio
    async def test_find_by_id_returns_entity(captured_pokemon_repository, trainer, pokemon):
        """Should return captured pokemon when id exists"""
        created = await captured_pokemon_repository.save(
            entity=CapturedPokemon(
                hp=MOCK_CAPTURED_POKEMON.hp,
                wins=MOCK_CAPTURED_POKEMON.wins,
                level=MOCK_CAPTURED_POKEMON.level,
                iv_hp=MOCK_CAPTURED_POKEMON.iv_hp,
                ev_hp=MOCK_CAPTURED_POKEMON.ev_hp,
                losses=MOCK_CAPTURED_POKEMON.losses,
                max_hp=MOCK_CAPTURED_POKEMON.max_hp,
                battles=MOCK_CAPTURED_POKEMON.battles,
                iv_speed=MOCK_CAPTURED_POKEMON.iv_speed,
                speed=MOCK_CAPTURED_POKEMON.speed,
                ev_speed=MOCK_CAPTURED_POKEMON.ev_speed,
                iv_attack=MOCK_CAPTURED_POKEMON.iv_attack,
                attack=MOCK_CAPTURED_POKEMON.attack,
                ev_attack=MOCK_CAPTURED_POKEMON.ev_attack,
                iv_defense=MOCK_CAPTURED_POKEMON.iv_defense,
                defense=MOCK_CAPTURED_POKEMON.defense,
                ev_defense=MOCK_CAPTURED_POKEMON.ev_defense,
                experience=MOCK_CAPTURED_POKEMON.experience,
                nickname=MOCK_CAPTURED_POKEMON.nickname,
                iv_special_attack=MOCK_CAPTURED_POKEMON.iv_special_attack,
                special_attack=MOCK_CAPTURED_POKEMON.special_attack,
                ev_special_attack=MOCK_CAPTURED_POKEMON.ev_special_attack,
                iv_special_defense=MOCK_CAPTURED_POKEMON.iv_special_defense,
                special_defense=MOCK_CAPTURED_POKEMON.special_defense,
                ev_special_defense=MOCK_CAPTURED_POKEMON.ev_special_defense,
                captured_at=MOCK_CAPTURED_POKEMON.captured_at,
                pokemon_id=pokemon.id,
                trainer_id=trainer.id,
                formula=MOCK_CAPTURED_POKEMON.formula,
            )
        )

        result = await captured_pokemon_repository.find_by(id=created.id)

        assert result is not None
        assert result.id == created.id

    @staticmethod
    @pytest.mark.asyncio
    async def test_find_by_id_returns_none_when_missing(captured_pokemon_repository):
        """Should return None when captured pokemon id does not exist"""
        non_existent_id = '00000000-0000-0000-0000-000000000000'
        result = await captured_pokemon_repository.find_by(id=non_existent_id)

        assert result is None
