from datetime import datetime
from uuid import uuid4

import factory
import pytest_asyncio
from factory import Faker

from app.domain.captured_pokemon.model import CapturedPokemon
from app.domain.captured_pokemon.repository import CapturedPokemonRepository
from app.domain.captured_pokemon.service import CapturedPokemonService

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


@pytest_asyncio.fixture
async def captured_pokemon_repository(session):
    return CapturedPokemonRepository(session=session)


@pytest_asyncio.fixture
async def captured_pokemon_service(session):
    return CapturedPokemonService(session=session)


class CapturedPokemonFactory(factory.Factory):
    class Meta:
        model = CapturedPokemon

    hp = factory.Sequence(lambda n: n * MOCK_CAPTURED_POKEMON.hp)
    wins = factory.Sequence(lambda n: n)
    level = MOCK_CAPTURED_POKEMON.level
    iv_hp = factory.Sequence(lambda n: n * MOCK_CAPTURED_POKEMON.iv_hp)
    ev_hp = factory.Sequence(lambda n: n * MOCK_CAPTURED_POKEMON.ev_hp)
    losses = MOCK_CAPTURED_POKEMON.losses
    max_hp = factory.Sequence(lambda n: n * MOCK_CAPTURED_POKEMON.max_hp)
    battles = MOCK_CAPTURED_POKEMON.battles
    iv_speed = factory.Sequence(lambda n: n * MOCK_CAPTURED_POKEMON.iv_speed)
    ev_speed = factory.Sequence(lambda n: n * MOCK_CAPTURED_POKEMON.ev_speed)
    iv_attack = factory.Sequence(lambda n: n * MOCK_CAPTURED_POKEMON.iv_attack)
    ev_attack = factory.Sequence(lambda n: n * MOCK_CAPTURED_POKEMON.ev_attack)
    iv_defense = factory.Sequence(lambda n: n * MOCK_CAPTURED_POKEMON.iv_defense)
    ev_defense = factory.Sequence(lambda n: n * MOCK_CAPTURED_POKEMON.ev_defense)
    experience = factory.Sequence(lambda n: n * MOCK_CAPTURED_POKEMON.experience)
    nickname = Faker('name')
    iv_special_attack = factory.Sequence(lambda n: n * MOCK_CAPTURED_POKEMON.iv_special_attack)
    ev_special_attack = factory.Sequence(lambda n: n * MOCK_CAPTURED_POKEMON.ev_special_attack)
    iv_special_defense = factory.Sequence(
        lambda n: n * MOCK_CAPTURED_POKEMON.iv_special_defense
    )
    ev_special_defense = factory.Sequence(
        lambda n: n * MOCK_CAPTURED_POKEMON.ev_special_defense
    )
    captured_at = MOCK_CAPTURED_POKEMON.captured_at
    pokemon_id = factory.LazyAttribute(lambda o: str(uuid4()))
    trainer_id = factory.LazyAttribute(lambda o: str(uuid4()))
