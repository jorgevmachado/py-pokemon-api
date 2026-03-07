import factory
from factory import Faker

from app.domain.pokedex.model import Pokedex


class PokedexFactory(factory.Factory):
    class Meta:
        model = Pokedex

    hp = factory.Sequence(lambda n: 50 + n)
    wins = 0
    level = 1
    iv_hp = factory.Sequence(lambda n: 20 + (n % 11))
    ev_hp = factory.Sequence(lambda n: 100 + (n % 53))
    losses = 0
    max_hp = factory.LazyAttribute(lambda o: o.hp)
    battles = 0
    nickname = Faker('first_name')
    speed = factory.Sequence(lambda n: 45 + (n % 36))
    iv_speed = factory.Sequence(lambda n: 20 + (n % 11))
    ev_speed = factory.Sequence(lambda n: 50 + (n % 53))
    attack = factory.Sequence(lambda n: 50 + (n % 35))
    iv_attack = factory.Sequence(lambda n: 15 + (n % 16))
    ev_attack = factory.Sequence(lambda n: 80 + (n % 53))
    defense = factory.Sequence(lambda n: 49 + (n % 36))
    iv_defense = factory.Sequence(lambda n: 20 + (n % 11))
    ev_defense = factory.Sequence(lambda n: 100 + (n % 53))
    experience = 0
    special_attack = factory.Sequence(lambda n: 65 + (n % 45))
    iv_special_attack = factory.Sequence(lambda n: 25 + (n % 6))
    ev_special_attack = factory.Sequence(lambda n: 60 + (n % 53))
    special_defense = factory.Sequence(lambda n: 65 + (n % 36))
    iv_special_defense = factory.Sequence(lambda n: 20 + (n % 11))
    ev_special_defense = factory.Sequence(lambda n: 80 + (n % 53))
    discovered = False
    formula = 'x**3'
    trainer_id = factory.Faker('uuid4')
    pokemon_id = factory.Faker('uuid4')
