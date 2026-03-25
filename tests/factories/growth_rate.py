import factory
from factory import Faker

from app.models.pokemon_growth_rate import PokemonGrowthRate


class PokemonGrowthRateFactory(factory.Factory):
    class Meta:
        model = PokemonGrowthRate

    url = factory.LazyAttribute(lambda o: f'https://pokeapi.co/api/v2/growth-rate/{o.order}/')
    name = Faker('name')
    order = factory.Sequence(lambda n: n)
    formula = '\\frac{6x^3}{5} - 15x^2 + 100x - 140'
    description = Faker('text')
