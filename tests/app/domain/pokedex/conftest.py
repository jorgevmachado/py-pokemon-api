import random
from uuid import uuid4

import factory
import pytest_asyncio
from factory import Faker

from app.domain.pokedex.model import Pokedex
from app.domain.pokedex.repository import PokedexRepository
from app.domain.pokedex.service import PokedexService


@pytest_asyncio.fixture
async def pokedex_repository(session):
    return PokedexRepository(session=session)


@pytest_asyncio.fixture
async def pokedex_service(session):
    return PokedexService(session=session)

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

class PokedexFactory(factory.Factory):
    class Meta:
        model = Pokedex

    hp = factory.Sequence(lambda n: n * MOCK_POKEDEX.hp)
    wins = factory.Sequence(lambda n: n)
    level = MOCK_POKEDEX.level
    iv_hp = factory.Sequence(lambda n: n * MOCK_POKEDEX.iv_hp)
    ev_hp = factory.Sequence(lambda n: n * MOCK_POKEDEX.ev_hp)
    losses = MOCK_POKEDEX.losses
    max_hp = factory.Sequence(lambda n: n * MOCK_POKEDEX.max_hp)
    battles = MOCK_POKEDEX.battles
    iv_speed = factory.Sequence(lambda n: n * MOCK_POKEDEX.iv_speed)
    ev_speed = factory.Sequence(lambda n: n * MOCK_POKEDEX.ev_speed)
    iv_attack = factory.Sequence(lambda n: n * MOCK_POKEDEX.iv_attack)
    ev_attack = factory.Sequence(lambda n: n * MOCK_POKEDEX.ev_attack)
    iv_defense = factory.Sequence(lambda n: n * MOCK_POKEDEX.iv_defense)
    ev_defense = factory.Sequence(lambda n: n * MOCK_POKEDEX.ev_defense)
    experience = factory.Sequence(lambda n: n * MOCK_POKEDEX.experience)
    nickname = Faker('name')
    iv_special_attack = factory.Sequence(lambda n: n * MOCK_POKEDEX.iv_special_attack)
    ev_special_attack = factory.Sequence(lambda n: n * MOCK_POKEDEX.ev_special_attack)
    iv_special_defense = factory.Sequence(lambda n: n * MOCK_POKEDEX.iv_special_defense)
    ev_special_defense = factory.Sequence(lambda n: n * MOCK_POKEDEX.ev_special_defense)
    discovered = factory.LazyAttribute(lambda o: random.choice([True, False]))
    pokemon_id = factory.LazyAttribute(lambda o: str(uuid4()))
    trainer_id = factory.LazyAttribute(lambda o: str(uuid4()))
