from datetime import datetime
from uuid import uuid4

import factory
from factory import Faker

from app.domain.captured_pokemon.model import CapturedPokemon

MOCK_CAPTURED_POKEMON = CapturedPokemon(
    hp=12,
    wins=0,
    level=1,
    iv_hp=17,
    ev_hp=110,
    losses=0,
    max_hp=12,
    battles=0,
    nickname='bulbasaur',
    speed=6,
    iv_speed=2,
    ev_speed=184,
    attack=6,
    iv_attack=24,
    ev_attack=26,
    defense=6,
    iv_defense=13,
    ev_defense=108,
    experience=0,
    special_attack=6,
    iv_special_attack=22,
    ev_special_attack=39,
    special_defense=6,
    iv_special_defense=17,
    ev_special_defense=23,
    captured_at=datetime.now(),
    pokemon_id='9efd7c0a-7fa8-402a-8166-ff85b82cac33',
    trainer_id='6129c647-9823-48c1-a09e-7f471497a0e9',
    formula='\frac{6x^3}{5} - 15x^2 + 100x - 140',
)


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
    speed = factory.Sequence(lambda n: n * MOCK_CAPTURED_POKEMON.speed)
    ev_speed = factory.Sequence(lambda n: n * MOCK_CAPTURED_POKEMON.ev_speed)
    iv_attack = factory.Sequence(lambda n: n * MOCK_CAPTURED_POKEMON.iv_attack)
    attack = factory.Sequence(lambda n: n * MOCK_CAPTURED_POKEMON.attack)
    ev_attack = factory.Sequence(lambda n: n * MOCK_CAPTURED_POKEMON.ev_attack)
    iv_defense = factory.Sequence(lambda n: n * MOCK_CAPTURED_POKEMON.iv_defense)
    defense = factory.Sequence(lambda n: n * MOCK_CAPTURED_POKEMON.defense)
    ev_defense = factory.Sequence(lambda n: n * MOCK_CAPTURED_POKEMON.ev_defense)
    experience = factory.Sequence(lambda n: n * MOCK_CAPTURED_POKEMON.experience)
    nickname = Faker('name')
    iv_special_attack = factory.Sequence(lambda n: n * MOCK_CAPTURED_POKEMON.iv_special_attack)
    special_attack = factory.Sequence(lambda n: n * MOCK_CAPTURED_POKEMON.special_attack)
    ev_special_attack = factory.Sequence(lambda n: n * MOCK_CAPTURED_POKEMON.ev_special_attack)
    iv_special_defense = factory.Sequence(
        lambda n: n * MOCK_CAPTURED_POKEMON.iv_special_defense
    )
    special_defense = factory.Sequence(lambda n: n * MOCK_CAPTURED_POKEMON.special_defense)
    ev_special_defense = factory.Sequence(
        lambda n: n * MOCK_CAPTURED_POKEMON.ev_special_defense
    )
    captured_at = MOCK_CAPTURED_POKEMON.captured_at
    pokemon_id = factory.LazyAttribute(lambda o: str(uuid4()))
    trainer_id = factory.LazyAttribute(lambda o: str(uuid4()))
    formula = '\frac{6x^3}{5} - 15x^2 + 100x - 140'
