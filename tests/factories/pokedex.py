import random
from uuid import uuid4

import factory
from factory import Faker

from app.models.pokedex import Pokedex

MOCK_POKEDEX = Pokedex(
    nickname='bulbasaur',
    hp=12,
    wins=0,
    level=1,
    iv_hp=27,
    ev_hp=214,
    losses=0,
    max_hp=12,
    battles=0,
    speed=6,
    iv_speed=29,
    ev_speed=126,
    attack=6,
    iv_attack=10,
    ev_attack=157,
    defense=6,
    iv_defense=26,
    ev_defense=10,
    experience=0,
    special_attack=6,
    iv_special_attack=20,
    ev_special_attack=2,
    iv_special_defense=23,
    special_defense=6,
    ev_special_defense=0,
    discovered=True,
    pokemon_id='9efd7c0a-7fa8-402a-8166-ff85b82cac33',
    trainer_id='6129c647-9823-48c1-a09e-7f471497a0e9',
    formula='\frac{6x^3}{5} - 15x^2 + 100x - 140',
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
    speed = factory.Sequence(lambda n: n * MOCK_POKEDEX.speed)
    ev_speed = factory.Sequence(lambda n: n * MOCK_POKEDEX.ev_speed)
    iv_attack = factory.Sequence(lambda n: n * MOCK_POKEDEX.iv_attack)
    attack = factory.Sequence(lambda n: n * MOCK_POKEDEX.attack)
    ev_attack = factory.Sequence(lambda n: n * MOCK_POKEDEX.ev_attack)
    iv_defense = factory.Sequence(lambda n: n * MOCK_POKEDEX.iv_defense)
    defense = factory.Sequence(lambda n: n * MOCK_POKEDEX.defense)
    ev_defense = factory.Sequence(lambda n: n * MOCK_POKEDEX.ev_defense)
    experience = factory.Sequence(lambda n: n * MOCK_POKEDEX.experience)
    nickname = Faker('name')
    iv_special_attack = factory.Sequence(lambda n: n * MOCK_POKEDEX.iv_special_attack)
    special_attack = factory.Sequence(lambda n: n * MOCK_POKEDEX.special_attack)
    ev_special_attack = factory.Sequence(lambda n: n * MOCK_POKEDEX.ev_special_attack)
    iv_special_defense = factory.Sequence(lambda n: n * MOCK_POKEDEX.iv_special_defense)
    special_defense = factory.Sequence(lambda n: n * MOCK_POKEDEX.special_defense)
    ev_special_defense = factory.Sequence(lambda n: n * MOCK_POKEDEX.ev_special_defense)
    discovered = factory.LazyAttribute(lambda o: random.choice([True, False]))
    pokemon_id = factory.LazyAttribute(lambda o: str(uuid4()))
    trainer_id = factory.LazyAttribute(lambda o: str(uuid4()))
    formula = '\frac{6x^3}{5} - 15x^2 + 100x - 140'
