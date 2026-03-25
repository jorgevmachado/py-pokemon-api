import factory
from factory import Faker

from app.models.pokemon_move import PokemonMove


class PokemonMoveFactory(factory.Factory):
    class Meta:
        model = PokemonMove

    pp = factory.Sequence(lambda n: n * 15)
    url = factory.LazyAttribute(lambda o: f'https://pokeapi.co/api/v2/move/{o.order}/')
    type = Faker('name')
    name = Faker('name')
    order = factory.Sequence(lambda n: n)
    power = factory.Sequence(lambda n: n * 40)
    target = 'selected-pokemon'
    effect = 'This move deals damage to the target'
    priority = 0
    accuracy = 100
    short_effect = 'Deals damage'
    damage_class = 'special'
    effect_chance = None


MOCK_POKEMON_MOVE_MEGA_DRAIN = PokemonMoveFactory.build(
    pp=15, type='grass', name='Mega Drain', order=72, power=40
)
