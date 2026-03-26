import random

import factory
from factory import Faker

from app.models.pokemon_type import PokemonType


class PokemonTypeFactory(factory.Factory):
    class Meta:
        model = PokemonType

    url = factory.LazyAttribute(lambda o: f'https://pokeapi.co/api/v2/type/{o.order}/')
    name = Faker('name')
    order = factory.Sequence(lambda n: n)
    text_color = factory.LazyAttribute(lambda o: random.choice(['red', 'blue', 'green']))
    background_color = factory.LazyAttribute(lambda o: random.choice(['red', 'blue', 'green']))
