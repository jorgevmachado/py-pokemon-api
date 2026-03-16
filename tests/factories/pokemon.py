import random

import factory
from factory import Faker

from app.domain.pokemon.model import Pokemon
from app.shared.enums.status_enum import StatusEnum


class PokemonFactory(factory.Factory):
    class Meta:
        model = Pokemon

    url = factory.LazyAttribute(lambda o: f'https://pokeapi.co/api/v2/pokemon/{o.name}')
    name = Faker('name')
    order = factory.Sequence(lambda n: n)
    status = StatusEnum.COMPLETE
    external_image = factory.LazyAttribute(
        lambda o: f'https://pokeapi.co/api/v2/pokemon/{o.name}'
    )
    hp = factory.Sequence(lambda n: n * 45)
    image = factory.LazyAttribute(lambda o: f'https://pokeapi.co/api/v2/pokemon/{o.name}')
    speed = factory.Sequence(lambda n: n * 45)
    height = factory.Sequence(lambda n: n * 7)
    weight = factory.Sequence(lambda n: n * 69)
    attack = factory.Sequence(lambda n: n * 49)
    defense = factory.Sequence(lambda n: n * 65)
    habitat = 'grassland'
    is_baby = factory.LazyAttribute(lambda o: random.choice([True, False]))
    shape_url = factory.LazyAttribute(lambda o: f'https://pokeapi.co/api/v2/pokemon/{o.name}')
    shape_name = factory.LazyAttribute(lambda o: f'shape_name_{o.name}')
    is_mythical = factory.LazyAttribute(lambda o: random.choice([True, False]))
    gender_rate = factory.Sequence(lambda n: n * 1)
    is_legendary = factory.LazyAttribute(lambda o: random.choice([True, False]))
    capture_rate = factory.Sequence(lambda n: n * 69)
    hatch_counter = factory.Sequence(lambda n: n * 69)
    base_happiness = factory.Sequence(lambda n: n * 69)
    special_attack = factory.Sequence(lambda n: n * 65)
    base_experience = factory.Sequence(lambda n: n * 64)
    special_defense = factory.Sequence(lambda n: n * 65)
    evolution_chain_url = factory.LazyAttribute(
        lambda o: f'https://pokeapi.co/api/v2/pokemon/{o.name}'
    )
    evolves_from_species = factory.LazyAttribute(lambda o: f'evolves_from_species_{o.name}')
    has_gender_differences = factory.LazyAttribute(lambda o: random.choice([True, False]))


MOCK_POKEMON_BULBASAUR = PokemonFactory.build(
    name='bulbasaur',
    order=1,
    status=StatusEnum.COMPLETE,
    hp=45,
    speed=45,
    attack=49,
    defense=49,
    special_attack=65,
    special_defense=65,
)

MOCK_POKEMON_CHARIZARD = PokemonFactory.build(
    name='charizard',
    order=6,
    status=StatusEnum.COMPLETE,
    hp=78,
    speed=100,
    attack=84,
    defense=78,
    special_attack=109,
    special_defense=85,
)
