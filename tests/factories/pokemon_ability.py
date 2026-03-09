import random

import factory
from factory import Faker

from app.domain.ability.model import PokemonAbility


class PokemonAbilityFactory(factory.Factory):
    class Meta:
        model = PokemonAbility

    url = factory.LazyAttribute(lambda o: f'https://pokeapi.co/api/v2/ability/{o.order}/')
    name = Faker('name')
    order = factory.Sequence(lambda n: n)
    slot = factory.Sequence(lambda n: n)
    is_hidden = factory.LazyAttribute(lambda o: random.choice([True, False]))
