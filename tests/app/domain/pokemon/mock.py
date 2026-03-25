from app.domain.pokemon.external.schemas import PokemonExternalBase
from app.domain.pokemon.schema import GeneratePokemonRelationshipSchema
from app.domain.type.model import PokemonType
from app.models.pokemon import Pokemon
from app.models.pokemon_ability import PokemonAbility
from app.models.pokemon_growth_rate import PokemonGrowthRate
from app.models.pokemon_move import PokemonMove
from app.shared.enums.status_enum import StatusEnum

MOCK_ENTITY_ORDER = 1
MOCK_POKEMON_MOVE_LIST = [
    PokemonMove(
        name='tackle',
        order=1,
        pp=35,
        url='https://pokeapi.co/api/v2/move/1/',
        type='normal',
        power=40,
        target='selected-pokemon',
        effect='Inflicts regular damage with no additional effect.',
        priority=0,
        accuracy=100,
        short_effect='Inflicts regular damage.',
        damage_class='physical',
        effect_chance=0,
    )
]
MOCK_POKEMON_TYPES_LIST = [
    PokemonType(
        name='grass',
        order=1,
        url='https://pokeapi.co/api/v2/type/12/',
        text_color='#ffffff',
        background_color='#78c850',
    )
]

MOCK_POKEMON_ABILITIES_LIST = [
    PokemonAbility(
        name='overgrow',
        order=1,
        url='https://pokeapi.co/api/v2/ability/65/',
        slot=1,
        is_hidden=False,
    )
]

MOCK_POKEMON_GROWTH_RATE = PokemonGrowthRate(
    name='medium-slow',
    order=1,
    url='https://pokeapi.co/api/v2/growth-rate/4/',
    formula='x^3',
    description='Slowly decreases in strength.',
)

MOCK_RELATIONSHIPS = GeneratePokemonRelationshipSchema(
    moves=[],
    types=[],
    abilities=[],
    growth_rate=PokemonExternalBase(
        url='https://pokeapi.co/api/v2/growth-rate/medium-slow/', name='medium-slow'
    ),
)

MOCK_ENTITY_POKEMON = Pokemon(
    url='https://pokeapi.co/api/v2/pokemon/1/',
    name='bulbasaur',
    order=MOCK_ENTITY_ORDER,
    status=StatusEnum.INCOMPLETE,
    external_image='https://example.com/bulbasaur.png',
    hp=None,
    image=None,
    speed=None,
    height=None,
    weight=None,
    attack=None,
    defense=None,
    habitat=None,
    is_baby=None,
    shape_url=None,
    shape_name=None,
    is_mythical=None,
    gender_rate=None,
    is_legendary=None,
    capture_rate=None,
    hatch_counter=None,
    base_happiness=None,
    special_attack=None,
    base_experience=None,
    special_defense=None,
    evolution_chain_url=None,
    evolves_from_species=None,
    has_gender_differences=None,
)
