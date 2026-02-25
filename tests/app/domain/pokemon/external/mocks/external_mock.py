from datetime import datetime

from app.domain.pokemon.external.schemas import (
    PokemonExternalBase,
    PokemonExternalBaseAbilitySchemaResponse,
    PokemonExternalBaseMoveSchemaResponse,
    PokemonExternalBaseTypeSchemaResponse,
    PokemonExternalByNameSchemaResponse,
    PokemonExternalByNameSpritesDreamWorldSchema,
    PokemonExternalByNameSpritesOtherSchemaResponse,
    PokemonExternalByNameSpritesSchemaResponse,
    PokemonExternalByNameStatsSchemaResponse,
    PokemonExternalSpecieSchemaResponse,
    PokemonSpecieEvolutionChainResponse,
)
from app.domain.pokemon.schema import PokemonSchema
from app.shared.status_enum import StatusEnum
from tests.app.domain.pokemon.external.mocks.business_mock import (
    MOCK_ATTRIBUTES_ATTACK,
    MOCK_ATTRIBUTES_DEFENSE,
    MOCK_ATTRIBUTES_HP,
    MOCK_ATTRIBUTES_SPECIAL_ATTACK,
    MOCK_ATTRIBUTES_SPECIAL_DEFENSE,
    MOCK_ATTRIBUTES_SPEED,
)

MOCK_POKEMON_NAME = 'bulbasaur'
MOCK_POKEMON_IMAGE = 'https://example.com/bulbasaur.png'
MOCK_POKEMON_HEIGHT = 7
MOCK_POKEMON_WEIGHT = 69
MOCK_POKEMON_BASE_EXPERIENCE = 64
MOCK_INITIAL_POKEMON = PokemonSchema(
    id='mock-pokemon-id',
    url='https://pokeapi.co/api/v2/pokemon/1/',
    name=MOCK_POKEMON_NAME,
    order=1,
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
    created_at=datetime.now(),
    updated_at=datetime.now(),
    deleted_at=None,
)
MOCK_RESPONSE_TYPE = PokemonExternalBaseTypeSchemaResponse(
    slot=1,
    type=PokemonExternalBase(
        name='grass',
        url='https://pokeapi.co/api/v2/type/12/',
    ),
)
MOCK_RESPONSE_MOVE = PokemonExternalBaseMoveSchemaResponse(
    move=PokemonExternalBase(
        name='razor-wind',
        url='https://pokeapi.co/api/v2/move/13/',
    )
)
MOCK_RESPONSE_ABILITY = PokemonExternalBaseAbilitySchemaResponse(
    ability=PokemonExternalBase(
        name='overgrow',
        url='https://pokeapi.co/api/v2/ability/65/',
    ),
    is_hidden=False,
    slot=1,
)

MOCK_RESPONSE_BY_NAME_SPRITES = PokemonExternalByNameSpritesSchemaResponse(
    front_default=MOCK_POKEMON_IMAGE,
    other=PokemonExternalByNameSpritesOtherSchemaResponse(
        dream_world=PokemonExternalByNameSpritesDreamWorldSchema(
            front_default=MOCK_POKEMON_IMAGE,
        )
    ),
)

MOCK_RESPONSE_BY_NAME_SPRITES_DREAM_WORLD = PokemonExternalByNameSpritesSchemaResponse(
    front_default=None,
    other=PokemonExternalByNameSpritesOtherSchemaResponse(
        dream_world=PokemonExternalByNameSpritesDreamWorldSchema(
            front_default=MOCK_POKEMON_IMAGE,
        )
    ),
)

MOCK_RESPONSE_BY_NAME_DATA = {
    'name': MOCK_POKEMON_NAME,
    'order': 1,
    'height': MOCK_POKEMON_HEIGHT,
    'weight': MOCK_POKEMON_WEIGHT,
    'base_experience': MOCK_POKEMON_BASE_EXPERIENCE,
    'types': [
        {
            'slot': 1,
            'type': {
                'name': 'grass',
                'url': 'https://pokeapi.co/api/v2/type/12/',
            },
        }
    ],
    'moves': [
        {
            'move': {
                'name': 'razor-wind',
                'url': 'https://pokeapi.co/api/v2/move/13/',
            },
            'version_group_details': [
                {
                    'level_learned_at': 0,
                    'move_learn_method': {
                        'name': 'egg',
                        'url': 'https://pokeapi.co/api/v2/move-learn-method/2/',
                    },
                    'order': None,
                    'version_group': {
                        'name': 'gold-silver',
                        'url': 'https://pokeapi.co/api/v2/version-group/3/',
                    },
                },
                {
                    'level_learned_at': 0,
                    'move_learn_method': {
                        'name': 'egg',
                        'url': 'https://pokeapi.co/api/v2/move-learn-method/2/',
                    },
                    'order': None,
                    'version_group': {
                        'name': 'crystal',
                        'url': 'https://pokeapi.co/api/v2/version-group/4/',
                    },
                },
            ],
        }
    ],
    'stats': [
        {
            'base_stat': 45,
            'effort': 0,
            'stat': {
                'name': 'hp',
                'url': 'https://pokeapi.co/api/v2/stat/1/',
            },
        },
        {
            'base_stat': 49,
            'effort': 0,
            'stat': {
                'name': 'attack',
                'url': 'https://pokeapi.co/api/v2/stat/2/',
            },
        },
        {
            'base_stat': 49,
            'effort': 0,
            'stat': {
                'name': 'defense',
                'url': 'https://pokeapi.co/api/v2/stat/3/',
            },
        },
        {
            'base_stat': 65,
            'effort': 1,
            'stat': {
                'name': 'special-attack',
                'url': 'https://pokeapi.co/api/v2/stat/4/',
            },
        },
        {
            'base_stat': 65,
            'effort': 0,
            'stat': {
                'name': 'special-defense',
                'url': 'https://pokeapi.co/api/v2/stat/5/',
            },
        },
        {
            'base_stat': 45,
            'effort': 0,
            'stat': {
                'name': 'speed',
                'url': 'https://pokeapi.co/api/v2/stat/6/',
            },
        },
    ],
    'abilities': [
        {
            'ability': {
                'name': 'overgrow',
                'url': 'https://pokeapi.co/api/v2/ability/65/',
            },
            'is_hidden': False,
            'slot': 1,
        }
    ],
    'sprites': {'front_default': MOCK_RESPONSE_BY_NAME_SPRITES.front_default},
}

MOCK_RESPONSE_BY_NAME_STATS = [
    PokemonExternalByNameStatsSchemaResponse(
        base_stat=MOCK_ATTRIBUTES_HP,
        stat=PokemonExternalBase(
            name='hp',
            url='https://pokeapi.co/api/v2/stat/1/',
        ),
    ),
    PokemonExternalByNameStatsSchemaResponse(
        base_stat=MOCK_ATTRIBUTES_ATTACK,
        stat=PokemonExternalBase(
            name='attack',
            url='https://pokeapi.co/api/v2/stat/2/',
        ),
    ),
    PokemonExternalByNameStatsSchemaResponse(
        base_stat=MOCK_ATTRIBUTES_DEFENSE,
        stat=PokemonExternalBase(
            name='defense',
            url='https://pokeapi.co/api/v2/stat/3/',
        ),
    ),
    PokemonExternalByNameStatsSchemaResponse(
        base_stat=MOCK_ATTRIBUTES_SPECIAL_ATTACK,
        stat=PokemonExternalBase(
            name='special-attack',
            url='https://pokeapi.co/api/v2/stat/4/',
        ),
    ),
    PokemonExternalByNameStatsSchemaResponse(
        base_stat=MOCK_ATTRIBUTES_SPECIAL_DEFENSE,
        stat=PokemonExternalBase(
            name='special-defense',
            url='https://pokeapi.co/api/v2/stat/5/',
        ),
    ),
    PokemonExternalByNameStatsSchemaResponse(
        base_stat=MOCK_ATTRIBUTES_SPEED,
        stat=PokemonExternalBase(
            name='speed',
            url='https://pokeapi.co/api/v2/stat/6/',
        ),
    ),
]

MOCK_RESPONSE_BY_NAME = PokemonExternalByNameSchemaResponse(
    name=MOCK_POKEMON_NAME,
    order=1,
    height=MOCK_POKEMON_HEIGHT,
    weight=MOCK_POKEMON_WEIGHT,
    base_experience=MOCK_POKEMON_BASE_EXPERIENCE,
    types=[MOCK_RESPONSE_TYPE],
    moves=[MOCK_RESPONSE_MOVE],
    stats=MOCK_RESPONSE_BY_NAME_STATS,
    abilities=[MOCK_RESPONSE_ABILITY],
    sprites=MOCK_RESPONSE_BY_NAME_SPRITES,
)

MOCK_RESPONSE_BY_SPECIE_DATA = {
    'name': MOCK_POKEMON_NAME,
    'shape': {
        'name': 'quadruped',
        'url': 'https://pokeapi.co/api/v2/pokemon-shape/8/',
    },
    'habitat': {
        'name': 'grassland',
        'url': 'https://pokeapi.co/api/v2/pokemon-habitat/3/',
    },
    'is_baby': False,
    'growth_rate': {
        'name': 'medium-slow',
        'url': 'https://pokeapi.co/api/v2/growth-rate/4/',
    },
    'gender_rate': 1,
    'is_mythical': False,
    'capture_rate': 45,
    'is_legendary': False,
    'hatch_counter': 20,
    'base_happiness': 70,
    'evolution_chain': {'url': 'https://pokeapi.co/api/v2/evolution-chain/1/'},
    'evolves_from_species': None,
    'has_gender_differences': False,
}
MOCK_RESPONSE_BY_SPECIE = PokemonExternalSpecieSchemaResponse(
    name=MOCK_POKEMON_NAME,
    shape=PokemonExternalBase(
        name='quadruped',
        url='https://pokeapi.co/api/v2/pokemon-shape/8/',
    ),
    habitat=PokemonExternalBase(
        name='grassland',
        url='https://pokeapi.co/api/v2/pokemon-habitat/3/',
    ),
    is_baby=False,
    growth_rate=PokemonExternalBase(
        name='medium-slow',
        url='https://pokeapi.co/api/v2/growth-rate/4/',
    ),
    gender_rate=1,
    is_mythical=False,
    capture_rate=45,
    is_legendary=False,
    hatch_counter=20,
    base_happiness=70,
    evolution_chain=PokemonSpecieEvolutionChainResponse(
        url='https://pokeapi.co/api/v2/evolution-chain/1/'
    ),
    evolves_from_species=PokemonExternalBase(
        name='fire',
        url='https://pokeapi.co/api/v2/specie/4/',
    ),
    has_gender_differences=False,
)

MOCK_RESPONSE_BY_MOVE_DATA = {
    'name': MOCK_POKEMON_NAME,
    'accuracy': 95,
    'contest_combos': {
        'normal': {
            'use_after': [
                {
                    'name': 'swords-dance',
                    'url': 'https://pokeapi.co/api/v2/move/14/',
                }
            ],
            'use_before': None,
        },
        'super': {'use_after': None, 'use_before': None},
    },
    'contest_effect': {'url': 'https://pokeapi.co/api/v2/contest-effect/14/'},
    'contest_type': {
        'name': 'cool',
        'url': 'https://pokeapi.co/api/v2/contest-type/1/',
    },
    'damage_class': {
        'name': 'physical',
        'url': 'https://pokeapi.co/api/v2/move-damage-class/2/',
    },
    'effect_chance': None,
    'effect_changes': [],
    'effect_entries': [
        {
            'effect': 'Inflige des [dégats réguliers.',
            'language': {
                'name': 'fr',
                'url': 'https://pokeapi.co/api/v2/language/5/',
            },
            'short_effect': 'Inflige des dégâts réguliers.',
        },
        {
            'effect': 'Inflicts regular damage.',
            'language': {
                'name': 'en',
                'url': 'https://pokeapi.co/api/v2/language/9/',
            },
            'short_effect': 'Inflicts regular damage.',
        },
    ],
    'flavor_text_entries': [
        {
            'flavor_text': 'Cuts using claws,\nscythes, etc.',
            'language': {
                'name': 'en',
                'url': 'https://pokeapi.co/api/v2/language/9/',
            },
            'version_group': {
                'name': 'gold-silver',
                'url': 'https://pokeapi.co/api/v2/version-group/3/',
            },
        }
    ],
    'generation': {
        'name': 'generation-i',
        'url': 'https://pokeapi.co/api/v2/generation/1/',
    },
    'id': 15,
    'learned_by_pokemon': [
        {
            'name': 'bulbasaur',
            'url': 'https://pokeapi.co/api/v2/pokemon/1/',
        },
        {
            'name': 'ivysaur',
            'url': 'https://pokeapi.co/api/v2/pokemon/2/',
        },
        {
            'name': 'venusaur',
            'url': 'https://pokeapi.co/api/v2/pokemon/3/',
        },
        {
            'name': 'charmander',
            'url': 'https://pokeapi.co/api/v2/pokemon/4/',
        },
        {
            'name': 'charmeleon',
            'url': 'https://pokeapi.co/api/v2/pokemon/5/',
        },
        {
            'name': 'charizard',
            'url': 'https://pokeapi.co/api/v2/pokemon/6/',
        },
        {
            'name': 'beedrill',
            'url': 'https://pokeapi.co/api/v2/pokemon/15/',
        },
        {
            'name': 'rattata',
            'url': 'https://pokeapi.co/api/v2/pokemon/19/',
        },
        {
            'name': 'raticate',
            'url': 'https://pokeapi.co/api/v2/pokemon/20/',
        },
        {
            'name': 'sandshrew',
            'url': 'https://pokeapi.co/api/v2/pokemon/27/',
        },
        {
            'name': 'sandslash',
            'url': 'https://pokeapi.co/api/v2/pokemon/28/',
        },
        {
            'name': 'nidoran-f',
            'url': 'https://pokeapi.co/api/v2/pokemon/29/',
        },
        {
            'name': 'nidorina',
            'url': 'https://pokeapi.co/api/v2/pokemon/30/',
        },
        {
            'name': 'nidoqueen',
            'url': 'https://pokeapi.co/api/v2/pokemon/31/',
        },
        {
            'name': 'nidoran-m',
            'url': 'https://pokeapi.co/api/v2/pokemon/32/',
        },
        {
            'name': 'nidorino',
            'url': 'https://pokeapi.co/api/v2/pokemon/33/',
        },
        {
            'name': 'nidoking',
            'url': 'https://pokeapi.co/api/v2/pokemon/34/',
        },
        {
            'name': 'oddish',
            'url': 'https://pokeapi.co/api/v2/pokemon/43/',
        },
        {'name': 'gloom', 'url': 'https://pokeapi.co/api/v2/pokemon/44/'},
        {
            'name': 'vileplume',
            'url': 'https://pokeapi.co/api/v2/pokemon/45/',
        },
        {'name': 'paras', 'url': 'https://pokeapi.co/api/v2/pokemon/46/'},
        {
            'name': 'parasect',
            'url': 'https://pokeapi.co/api/v2/pokemon/47/',
        },
        {
            'name': 'diglett',
            'url': 'https://pokeapi.co/api/v2/pokemon/50/',
        },
        {
            'name': 'dugtrio',
            'url': 'https://pokeapi.co/api/v2/pokemon/51/',
        },
        {
            'name': 'meowth',
            'url': 'https://pokeapi.co/api/v2/pokemon/52/',
        },
        {
            'name': 'persian',
            'url': 'https://pokeapi.co/api/v2/pokemon/53/',
        },
        {
            'name': 'bellsprout',
            'url': 'https://pokeapi.co/api/v2/pokemon/69/',
        },
        {
            'name': 'weepinbell',
            'url': 'https://pokeapi.co/api/v2/pokemon/70/',
        },
        {
            'name': 'victreebel',
            'url': 'https://pokeapi.co/api/v2/pokemon/71/',
        },
        {
            'name': 'tentacool',
            'url': 'https://pokeapi.co/api/v2/pokemon/72/',
        },
        {
            'name': 'tentacruel',
            'url': 'https://pokeapi.co/api/v2/pokemon/73/',
        },
        {
            'name': 'farfetchd',
            'url': 'https://pokeapi.co/api/v2/pokemon/83/',
        },
        {
            'name': 'krabby',
            'url': 'https://pokeapi.co/api/v2/pokemon/98/',
        },
        {
            'name': 'kingler',
            'url': 'https://pokeapi.co/api/v2/pokemon/99/',
        },
        {
            'name': 'lickitung',
            'url': 'https://pokeapi.co/api/v2/pokemon/108/',
        },
        {
            'name': 'rhydon',
            'url': 'https://pokeapi.co/api/v2/pokemon/112/',
        },
        {
            'name': 'tangela',
            'url': 'https://pokeapi.co/api/v2/pokemon/114/',
        },
        {
            'name': 'kangaskhan',
            'url': 'https://pokeapi.co/api/v2/pokemon/115/',
        },
        {
            'name': 'scyther',
            'url': 'https://pokeapi.co/api/v2/pokemon/123/',
        },
        {
            'name': 'pinsir',
            'url': 'https://pokeapi.co/api/v2/pokemon/127/',
        },
        {
            'name': 'kabutops',
            'url': 'https://pokeapi.co/api/v2/pokemon/141/',
        },
        {
            'name': 'dragonite',
            'url': 'https://pokeapi.co/api/v2/pokemon/149/',
        },
        {'name': 'mew', 'url': 'https://pokeapi.co/api/v2/pokemon/151/'},
        {
            'name': 'chikorita',
            'url': 'https://pokeapi.co/api/v2/pokemon/152/',
        },
        {
            'name': 'bayleef',
            'url': 'https://pokeapi.co/api/v2/pokemon/153/',
        },
        {
            'name': 'meganium',
            'url': 'https://pokeapi.co/api/v2/pokemon/154/',
        },
        {
            'name': 'cyndaquil',
            'url': 'https://pokeapi.co/api/v2/pokemon/155/',
        },
        {
            'name': 'quilava',
            'url': 'https://pokeapi.co/api/v2/pokemon/156/',
        },
        {
            'name': 'typhlosion',
            'url': 'https://pokeapi.co/api/v2/pokemon/157/',
        },
        {
            'name': 'totodile',
            'url': 'https://pokeapi.co/api/v2/pokemon/158/',
        },
        {
            'name': 'croconaw',
            'url': 'https://pokeapi.co/api/v2/pokemon/159/',
        },
        {
            'name': 'feraligatr',
            'url': 'https://pokeapi.co/api/v2/pokemon/160/',
        },
        {
            'name': 'sentret',
            'url': 'https://pokeapi.co/api/v2/pokemon/161/',
        },
        {
            'name': 'furret',
            'url': 'https://pokeapi.co/api/v2/pokemon/162/',
        },
        {
            'name': 'bellossom',
            'url': 'https://pokeapi.co/api/v2/pokemon/182/',
        },
        {
            'name': 'aipom',
            'url': 'https://pokeapi.co/api/v2/pokemon/190/',
        },
        {
            'name': 'sunkern',
            'url': 'https://pokeapi.co/api/v2/pokemon/191/',
        },
        {
            'name': 'sunflora',
            'url': 'https://pokeapi.co/api/v2/pokemon/192/',
        },
        {
            'name': 'espeon',
            'url': 'https://pokeapi.co/api/v2/pokemon/196/',
        },
        {
            'name': 'umbreon',
            'url': 'https://pokeapi.co/api/v2/pokemon/197/',
        },
        {
            'name': 'gligar',
            'url': 'https://pokeapi.co/api/v2/pokemon/207/',
        },
        {
            'name': 'steelix',
            'url': 'https://pokeapi.co/api/v2/pokemon/208/',
        },
        {
            'name': 'scizor',
            'url': 'https://pokeapi.co/api/v2/pokemon/212/',
        },
        {
            'name': 'heracross',
            'url': 'https://pokeapi.co/api/v2/pokemon/214/',
        },
        {
            'name': 'sneasel',
            'url': 'https://pokeapi.co/api/v2/pokemon/215/',
        },
        {
            'name': 'teddiursa',
            'url': 'https://pokeapi.co/api/v2/pokemon/216/',
        },
        {
            'name': 'ursaring',
            'url': 'https://pokeapi.co/api/v2/pokemon/217/',
        },
        {
            'name': 'skarmory',
            'url': 'https://pokeapi.co/api/v2/pokemon/227/',
        },
        {
            'name': 'raikou',
            'url': 'https://pokeapi.co/api/v2/pokemon/243/',
        },
        {
            'name': 'entei',
            'url': 'https://pokeapi.co/api/v2/pokemon/244/',
        },
        {
            'name': 'suicune',
            'url': 'https://pokeapi.co/api/v2/pokemon/245/',
        },
        {
            'name': 'tyranitar',
            'url': 'https://pokeapi.co/api/v2/pokemon/248/',
        },
        {
            'name': 'celebi',
            'url': 'https://pokeapi.co/api/v2/pokemon/251/',
        },
        {
            'name': 'treecko',
            'url': 'https://pokeapi.co/api/v2/pokemon/252/',
        },
        {
            'name': 'grovyle',
            'url': 'https://pokeapi.co/api/v2/pokemon/253/',
        },
        {
            'name': 'sceptile',
            'url': 'https://pokeapi.co/api/v2/pokemon/254/',
        },
        {
            'name': 'torchic',
            'url': 'https://pokeapi.co/api/v2/pokemon/255/',
        },
        {
            'name': 'combusken',
            'url': 'https://pokeapi.co/api/v2/pokemon/256/',
        },
        {
            'name': 'blaziken',
            'url': 'https://pokeapi.co/api/v2/pokemon/257/',
        },
        {
            'name': 'zigzagoon',
            'url': 'https://pokeapi.co/api/v2/pokemon/263/',
        },
        {
            'name': 'linoone',
            'url': 'https://pokeapi.co/api/v2/pokemon/264/',
        },
        {
            'name': 'nuzleaf',
            'url': 'https://pokeapi.co/api/v2/pokemon/274/',
        },
        {
            'name': 'shiftry',
            'url': 'https://pokeapi.co/api/v2/pokemon/275/',
        },
        {
            'name': 'breloom',
            'url': 'https://pokeapi.co/api/v2/pokemon/286/',
        },
        {
            'name': 'slakoth',
            'url': 'https://pokeapi.co/api/v2/pokemon/287/',
        },
        {
            'name': 'vigoroth',
            'url': 'https://pokeapi.co/api/v2/pokemon/288/',
        },
        {
            'name': 'slaking',
            'url': 'https://pokeapi.co/api/v2/pokemon/289/',
        },
        {
            'name': 'nincada',
            'url': 'https://pokeapi.co/api/v2/pokemon/290/',
        },
        {
            'name': 'ninjask',
            'url': 'https://pokeapi.co/api/v2/pokemon/291/',
        },
        {
            'name': 'shedinja',
            'url': 'https://pokeapi.co/api/v2/pokemon/292/',
        },
        {
            'name': 'sableye',
            'url': 'https://pokeapi.co/api/v2/pokemon/302/',
        },
        {'name': 'aron', 'url': 'https://pokeapi.co/api/v2/pokemon/304/'},
        {
            'name': 'lairon',
            'url': 'https://pokeapi.co/api/v2/pokemon/305/',
        },
        {
            'name': 'aggron',
            'url': 'https://pokeapi.co/api/v2/pokemon/306/',
        },
        {
            'name': 'roselia',
            'url': 'https://pokeapi.co/api/v2/pokemon/315/',
        },
        {
            'name': 'cacnea',
            'url': 'https://pokeapi.co/api/v2/pokemon/331/',
        },
        {
            'name': 'cacturne',
            'url': 'https://pokeapi.co/api/v2/pokemon/332/',
        },
        {
            'name': 'corphish',
            'url': 'https://pokeapi.co/api/v2/pokemon/341/',
        },
        {
            'name': 'crawdaunt',
            'url': 'https://pokeapi.co/api/v2/pokemon/342/',
        },
        {
            'name': 'anorith',
            'url': 'https://pokeapi.co/api/v2/pokemon/347/',
        },
        {
            'name': 'armaldo',
            'url': 'https://pokeapi.co/api/v2/pokemon/348/',
        },
        {
            'name': 'kecleon',
            'url': 'https://pokeapi.co/api/v2/pokemon/352/',
        },
        {
            'name': 'tropius',
            'url': 'https://pokeapi.co/api/v2/pokemon/357/',
        },
        {
            'name': 'absol',
            'url': 'https://pokeapi.co/api/v2/pokemon/359/',
        },
        {
            'name': 'bagon',
            'url': 'https://pokeapi.co/api/v2/pokemon/371/',
        },
        {
            'name': 'shelgon',
            'url': 'https://pokeapi.co/api/v2/pokemon/372/',
        },
        {
            'name': 'salamence',
            'url': 'https://pokeapi.co/api/v2/pokemon/373/',
        },
        {
            'name': 'metang',
            'url': 'https://pokeapi.co/api/v2/pokemon/375/',
        },
        {
            'name': 'metagross',
            'url': 'https://pokeapi.co/api/v2/pokemon/376/',
        },
        {
            'name': 'latias',
            'url': 'https://pokeapi.co/api/v2/pokemon/380/',
        },
        {
            'name': 'latios',
            'url': 'https://pokeapi.co/api/v2/pokemon/381/',
        },
        {
            'name': 'groudon',
            'url': 'https://pokeapi.co/api/v2/pokemon/383/',
        },
        {
            'name': 'deoxys-normal',
            'url': 'https://pokeapi.co/api/v2/pokemon/386/',
        },
        {
            'name': 'turtwig',
            'url': 'https://pokeapi.co/api/v2/pokemon/387/',
        },
        {
            'name': 'grotle',
            'url': 'https://pokeapi.co/api/v2/pokemon/388/',
        },
        {
            'name': 'torterra',
            'url': 'https://pokeapi.co/api/v2/pokemon/389/',
        },
        {
            'name': 'chimchar',
            'url': 'https://pokeapi.co/api/v2/pokemon/390/',
        },
        {
            'name': 'monferno',
            'url': 'https://pokeapi.co/api/v2/pokemon/391/',
        },
        {
            'name': 'infernape',
            'url': 'https://pokeapi.co/api/v2/pokemon/392/',
        },
        {
            'name': 'piplup',
            'url': 'https://pokeapi.co/api/v2/pokemon/393/',
        },
        {
            'name': 'prinplup',
            'url': 'https://pokeapi.co/api/v2/pokemon/394/',
        },
        {
            'name': 'empoleon',
            'url': 'https://pokeapi.co/api/v2/pokemon/395/',
        },
        {
            'name': 'bidoof',
            'url': 'https://pokeapi.co/api/v2/pokemon/399/',
        },
        {
            'name': 'bibarel',
            'url': 'https://pokeapi.co/api/v2/pokemon/400/',
        },
        {
            'name': 'kricketune',
            'url': 'https://pokeapi.co/api/v2/pokemon/402/',
        },
        {
            'name': 'budew',
            'url': 'https://pokeapi.co/api/v2/pokemon/406/',
        },
        {
            'name': 'roserade',
            'url': 'https://pokeapi.co/api/v2/pokemon/407/',
        },
        {
            'name': 'rampardos',
            'url': 'https://pokeapi.co/api/v2/pokemon/409/',
        },
        {
            'name': 'vespiquen',
            'url': 'https://pokeapi.co/api/v2/pokemon/416/',
        },
        {
            'name': 'pachirisu',
            'url': 'https://pokeapi.co/api/v2/pokemon/417/',
        },
        {
            'name': 'ambipom',
            'url': 'https://pokeapi.co/api/v2/pokemon/424/',
        },
        {
            'name': 'drifloon',
            'url': 'https://pokeapi.co/api/v2/pokemon/425/',
        },
        {
            'name': 'drifblim',
            'url': 'https://pokeapi.co/api/v2/pokemon/426/',
        },
        {
            'name': 'buneary',
            'url': 'https://pokeapi.co/api/v2/pokemon/427/',
        },
        {
            'name': 'lopunny',
            'url': 'https://pokeapi.co/api/v2/pokemon/428/',
        },
        {
            'name': 'glameow',
            'url': 'https://pokeapi.co/api/v2/pokemon/431/',
        },
        {
            'name': 'purugly',
            'url': 'https://pokeapi.co/api/v2/pokemon/432/',
        },
        {
            'name': 'stunky',
            'url': 'https://pokeapi.co/api/v2/pokemon/434/',
        },
        {
            'name': 'skuntank',
            'url': 'https://pokeapi.co/api/v2/pokemon/435/',
        },
        {
            'name': 'gible',
            'url': 'https://pokeapi.co/api/v2/pokemon/443/',
        },
        {
            'name': 'gabite',
            'url': 'https://pokeapi.co/api/v2/pokemon/444/',
        },
        {
            'name': 'garchomp',
            'url': 'https://pokeapi.co/api/v2/pokemon/445/',
        },
        {
            'name': 'skorupi',
            'url': 'https://pokeapi.co/api/v2/pokemon/451/',
        },
        {
            'name': 'drapion',
            'url': 'https://pokeapi.co/api/v2/pokemon/452/',
        },
        {
            'name': 'toxicroak',
            'url': 'https://pokeapi.co/api/v2/pokemon/454/',
        },
        {
            'name': 'carnivine',
            'url': 'https://pokeapi.co/api/v2/pokemon/455/',
        },
        {
            'name': 'weavile',
            'url': 'https://pokeapi.co/api/v2/pokemon/461/',
        },
        {
            'name': 'lickilicky',
            'url': 'https://pokeapi.co/api/v2/pokemon/463/',
        },
        {
            'name': 'rhyperior',
            'url': 'https://pokeapi.co/api/v2/pokemon/464/',
        },
        {
            'name': 'tangrowth',
            'url': 'https://pokeapi.co/api/v2/pokemon/465/',
        },
        {
            'name': 'gliscor',
            'url': 'https://pokeapi.co/api/v2/pokemon/472/',
        },
        {
            'name': 'gallade',
            'url': 'https://pokeapi.co/api/v2/pokemon/475/',
        },
        {
            'name': 'dialga',
            'url': 'https://pokeapi.co/api/v2/pokemon/483/',
        },
        {
            'name': 'palkia',
            'url': 'https://pokeapi.co/api/v2/pokemon/484/',
        },
        {
            'name': 'giratina-altered',
            'url': 'https://pokeapi.co/api/v2/pokemon/487/',
        },
        {
            'name': 'darkrai',
            'url': 'https://pokeapi.co/api/v2/pokemon/491/',
        },
        {
            'name': 'arceus',
            'url': 'https://pokeapi.co/api/v2/pokemon/493/',
        },
        {
            'name': 'snivy',
            'url': 'https://pokeapi.co/api/v2/pokemon/495/',
        },
        {
            'name': 'servine',
            'url': 'https://pokeapi.co/api/v2/pokemon/496/',
        },
        {
            'name': 'serperior',
            'url': 'https://pokeapi.co/api/v2/pokemon/497/',
        },
        {
            'name': 'oshawott',
            'url': 'https://pokeapi.co/api/v2/pokemon/501/',
        },
        {
            'name': 'dewott',
            'url': 'https://pokeapi.co/api/v2/pokemon/502/',
        },
        {
            'name': 'samurott',
            'url': 'https://pokeapi.co/api/v2/pokemon/503/',
        },
        {
            'name': 'patrat',
            'url': 'https://pokeapi.co/api/v2/pokemon/504/',
        },
        {
            'name': 'watchog',
            'url': 'https://pokeapi.co/api/v2/pokemon/505/',
        },
        {
            'name': 'purrloin',
            'url': 'https://pokeapi.co/api/v2/pokemon/509/',
        },
        {
            'name': 'liepard',
            'url': 'https://pokeapi.co/api/v2/pokemon/510/',
        },
        {
            'name': 'pansage',
            'url': 'https://pokeapi.co/api/v2/pokemon/511/',
        },
        {
            'name': 'simisage',
            'url': 'https://pokeapi.co/api/v2/pokemon/512/',
        },
        {
            'name': 'pansear',
            'url': 'https://pokeapi.co/api/v2/pokemon/513/',
        },
        {
            'name': 'simisear',
            'url': 'https://pokeapi.co/api/v2/pokemon/514/',
        },
        {
            'name': 'panpour',
            'url': 'https://pokeapi.co/api/v2/pokemon/515/',
        },
        {
            'name': 'simipour',
            'url': 'https://pokeapi.co/api/v2/pokemon/516/',
        },
        {
            'name': 'drilbur',
            'url': 'https://pokeapi.co/api/v2/pokemon/529/',
        },
        {
            'name': 'excadrill',
            'url': 'https://pokeapi.co/api/v2/pokemon/530/',
        },
        {
            'name': 'sewaddle',
            'url': 'https://pokeapi.co/api/v2/pokemon/540/',
        },
        {
            'name': 'swadloon',
            'url': 'https://pokeapi.co/api/v2/pokemon/541/',
        },
        {
            'name': 'leavanny',
            'url': 'https://pokeapi.co/api/v2/pokemon/542/',
        },
        {
            'name': 'scolipede',
            'url': 'https://pokeapi.co/api/v2/pokemon/545/',
        },
        {
            'name': 'petilil',
            'url': 'https://pokeapi.co/api/v2/pokemon/548/',
        },
        {
            'name': 'lilligant',
            'url': 'https://pokeapi.co/api/v2/pokemon/549/',
        },
        {
            'name': 'basculin-red-striped',
            'url': 'https://pokeapi.co/api/v2/pokemon/550/',
        },
        {
            'name': 'sandile',
            'url': 'https://pokeapi.co/api/v2/pokemon/551/',
        },
        {
            'name': 'krokorok',
            'url': 'https://pokeapi.co/api/v2/pokemon/552/',
        },
        {
            'name': 'krookodile',
            'url': 'https://pokeapi.co/api/v2/pokemon/553/',
        },
        {
            'name': 'dwebble',
            'url': 'https://pokeapi.co/api/v2/pokemon/557/',
        },
        {
            'name': 'crustle',
            'url': 'https://pokeapi.co/api/v2/pokemon/558/',
        },
        {
            'name': 'archen',
            'url': 'https://pokeapi.co/api/v2/pokemon/566/',
        },
        {
            'name': 'archeops',
            'url': 'https://pokeapi.co/api/v2/pokemon/567/',
        },
        {
            'name': 'zorua',
            'url': 'https://pokeapi.co/api/v2/pokemon/570/',
        },
        {
            'name': 'zoroark',
            'url': 'https://pokeapi.co/api/v2/pokemon/571/',
        },
        {
            'name': 'sawsbuck',
            'url': 'https://pokeapi.co/api/v2/pokemon/586/',
        },
        {
            'name': 'emolga',
            'url': 'https://pokeapi.co/api/v2/pokemon/587/',
        },
        {
            'name': 'karrablast',
            'url': 'https://pokeapi.co/api/v2/pokemon/588/',
        },
        {
            'name': 'escavalier',
            'url': 'https://pokeapi.co/api/v2/pokemon/589/',
        },
        {
            'name': 'joltik',
            'url': 'https://pokeapi.co/api/v2/pokemon/595/',
        },
        {
            'name': 'galvantula',
            'url': 'https://pokeapi.co/api/v2/pokemon/596/',
        },
        {
            'name': 'ferrothorn',
            'url': 'https://pokeapi.co/api/v2/pokemon/598/',
        },
        {
            'name': 'eelektross',
            'url': 'https://pokeapi.co/api/v2/pokemon/604/',
        },
        {'name': 'axew', 'url': 'https://pokeapi.co/api/v2/pokemon/610/'},
        {
            'name': 'fraxure',
            'url': 'https://pokeapi.co/api/v2/pokemon/611/',
        },
        {
            'name': 'haxorus',
            'url': 'https://pokeapi.co/api/v2/pokemon/612/',
        },
        {
            'name': 'cubchoo',
            'url': 'https://pokeapi.co/api/v2/pokemon/613/',
        },
        {
            'name': 'beartic',
            'url': 'https://pokeapi.co/api/v2/pokemon/614/',
        },
        {
            'name': 'druddigon',
            'url': 'https://pokeapi.co/api/v2/pokemon/621/',
        },
        {
            'name': 'pawniard',
            'url': 'https://pokeapi.co/api/v2/pokemon/624/',
        },
        {
            'name': 'bisharp',
            'url': 'https://pokeapi.co/api/v2/pokemon/625/',
        },
        {
            'name': 'bouffalant',
            'url': 'https://pokeapi.co/api/v2/pokemon/626/',
        },
        {
            'name': 'rufflet',
            'url': 'https://pokeapi.co/api/v2/pokemon/627/',
        },
        {
            'name': 'braviary',
            'url': 'https://pokeapi.co/api/v2/pokemon/628/',
        },
        {
            'name': 'vullaby',
            'url': 'https://pokeapi.co/api/v2/pokemon/629/',
        },
        {
            'name': 'mandibuzz',
            'url': 'https://pokeapi.co/api/v2/pokemon/630/',
        },
        {
            'name': 'heatmor',
            'url': 'https://pokeapi.co/api/v2/pokemon/631/',
        },
        {
            'name': 'durant',
            'url': 'https://pokeapi.co/api/v2/pokemon/632/',
        },
        {
            'name': 'cobalion',
            'url': 'https://pokeapi.co/api/v2/pokemon/638/',
        },
        {
            'name': 'terrakion',
            'url': 'https://pokeapi.co/api/v2/pokemon/639/',
        },
        {
            'name': 'virizion',
            'url': 'https://pokeapi.co/api/v2/pokemon/640/',
        },
        {
            'name': 'reshiram',
            'url': 'https://pokeapi.co/api/v2/pokemon/643/',
        },
        {
            'name': 'zekrom',
            'url': 'https://pokeapi.co/api/v2/pokemon/644/',
        },
        {
            'name': 'kyurem',
            'url': 'https://pokeapi.co/api/v2/pokemon/646/',
        },
        {
            'name': 'keldeo-ordinary',
            'url': 'https://pokeapi.co/api/v2/pokemon/647/',
        },
        {
            'name': 'chespin',
            'url': 'https://pokeapi.co/api/v2/pokemon/650/',
        },
        {
            'name': 'quilladin',
            'url': 'https://pokeapi.co/api/v2/pokemon/651/',
        },
        {
            'name': 'chesnaught',
            'url': 'https://pokeapi.co/api/v2/pokemon/652/',
        },
        {
            'name': 'fennekin',
            'url': 'https://pokeapi.co/api/v2/pokemon/653/',
        },
        {
            'name': 'braixen',
            'url': 'https://pokeapi.co/api/v2/pokemon/654/',
        },
        {
            'name': 'delphox',
            'url': 'https://pokeapi.co/api/v2/pokemon/655/',
        },
        {
            'name': 'froakie',
            'url': 'https://pokeapi.co/api/v2/pokemon/656/',
        },
        {
            'name': 'frogadier',
            'url': 'https://pokeapi.co/api/v2/pokemon/657/',
        },
        {
            'name': 'greninja',
            'url': 'https://pokeapi.co/api/v2/pokemon/658/',
        },
        {
            'name': 'bunnelby',
            'url': 'https://pokeapi.co/api/v2/pokemon/659/',
        },
        {
            'name': 'diggersby',
            'url': 'https://pokeapi.co/api/v2/pokemon/660/',
        },
        {
            'name': 'pancham',
            'url': 'https://pokeapi.co/api/v2/pokemon/674/',
        },
        {
            'name': 'pangoro',
            'url': 'https://pokeapi.co/api/v2/pokemon/675/',
        },
        {
            'name': 'espurr',
            'url': 'https://pokeapi.co/api/v2/pokemon/677/',
        },
        {
            'name': 'meowstic-male',
            'url': 'https://pokeapi.co/api/v2/pokemon/678/',
        },
        {
            'name': 'honedge',
            'url': 'https://pokeapi.co/api/v2/pokemon/679/',
        },
        {
            'name': 'doublade',
            'url': 'https://pokeapi.co/api/v2/pokemon/680/',
        },
        {
            'name': 'aegislash-shield',
            'url': 'https://pokeapi.co/api/v2/pokemon/681/',
        },
        {
            'name': 'inkay',
            'url': 'https://pokeapi.co/api/v2/pokemon/686/',
        },
        {
            'name': 'malamar',
            'url': 'https://pokeapi.co/api/v2/pokemon/687/',
        },
        {
            'name': 'binacle',
            'url': 'https://pokeapi.co/api/v2/pokemon/688/',
        },
        {
            'name': 'barbaracle',
            'url': 'https://pokeapi.co/api/v2/pokemon/689/',
        },
        {
            'name': 'clauncher',
            'url': 'https://pokeapi.co/api/v2/pokemon/692/',
        },
        {
            'name': 'clawitzer',
            'url': 'https://pokeapi.co/api/v2/pokemon/693/',
        },
        {
            'name': 'helioptile',
            'url': 'https://pokeapi.co/api/v2/pokemon/694/',
        },
        {
            'name': 'heliolisk',
            'url': 'https://pokeapi.co/api/v2/pokemon/695/',
        },
        {
            'name': 'sylveon',
            'url': 'https://pokeapi.co/api/v2/pokemon/700/',
        },
        {
            'name': 'hawlucha',
            'url': 'https://pokeapi.co/api/v2/pokemon/701/',
        },
        {
            'name': 'dedenne',
            'url': 'https://pokeapi.co/api/v2/pokemon/702/',
        },
        {
            'name': 'klefki',
            'url': 'https://pokeapi.co/api/v2/pokemon/707/',
        },
        {
            'name': 'phantump',
            'url': 'https://pokeapi.co/api/v2/pokemon/708/',
        },
        {
            'name': 'trevenant',
            'url': 'https://pokeapi.co/api/v2/pokemon/709/',
        },
        {
            'name': 'noibat',
            'url': 'https://pokeapi.co/api/v2/pokemon/714/',
        },
        {
            'name': 'noivern',
            'url': 'https://pokeapi.co/api/v2/pokemon/715/',
        },
        {
            'name': 'xerneas',
            'url': 'https://pokeapi.co/api/v2/pokemon/716/',
        },
        {
            'name': 'yveltal',
            'url': 'https://pokeapi.co/api/v2/pokemon/717/',
        },
        {
            'name': 'volcanion',
            'url': 'https://pokeapi.co/api/v2/pokemon/721/',
        },
        {
            'name': 'kartana',
            'url': 'https://pokeapi.co/api/v2/pokemon/798/',
        },
        {
            'name': 'deoxys-attack',
            'url': 'https://pokeapi.co/api/v2/pokemon/10001/',
        },
        {
            'name': 'deoxys-defense',
            'url': 'https://pokeapi.co/api/v2/pokemon/10002/',
        },
        {
            'name': 'deoxys-speed',
            'url': 'https://pokeapi.co/api/v2/pokemon/10003/',
        },
        {
            'name': 'giratina-origin',
            'url': 'https://pokeapi.co/api/v2/pokemon/10007/',
        },
        {
            'name': 'basculin-blue-striped',
            'url': 'https://pokeapi.co/api/v2/pokemon/10016/',
        },
        {
            'name': 'kyurem-black',
            'url': 'https://pokeapi.co/api/v2/pokemon/10022/',
        },
        {
            'name': 'kyurem-white',
            'url': 'https://pokeapi.co/api/v2/pokemon/10023/',
        },
        {
            'name': 'keldeo-resolute',
            'url': 'https://pokeapi.co/api/v2/pokemon/10024/',
        },
        {
            'name': 'meowstic-female',
            'url': 'https://pokeapi.co/api/v2/pokemon/10025/',
        },
        {
            'name': 'aegislash-blade',
            'url': 'https://pokeapi.co/api/v2/pokemon/10026/',
        },
        {
            'name': 'venusaur-mega',
            'url': 'https://pokeapi.co/api/v2/pokemon/10033/',
        },
        {
            'name': 'charizard-mega-x',
            'url': 'https://pokeapi.co/api/v2/pokemon/10034/',
        },
        {
            'name': 'charizard-mega-y',
            'url': 'https://pokeapi.co/api/v2/pokemon/10035/',
        },
        {
            'name': 'kangaskhan-mega',
            'url': 'https://pokeapi.co/api/v2/pokemon/10039/',
        },
        {
            'name': 'pinsir-mega',
            'url': 'https://pokeapi.co/api/v2/pokemon/10040/',
        },
        {
            'name': 'scizor-mega',
            'url': 'https://pokeapi.co/api/v2/pokemon/10046/',
        },
        {
            'name': 'heracross-mega',
            'url': 'https://pokeapi.co/api/v2/pokemon/10047/',
        },
        {
            'name': 'tyranitar-mega',
            'url': 'https://pokeapi.co/api/v2/pokemon/10049/',
        },
        {
            'name': 'blaziken-mega',
            'url': 'https://pokeapi.co/api/v2/pokemon/10050/',
        },
        {
            'name': 'aggron-mega',
            'url': 'https://pokeapi.co/api/v2/pokemon/10053/',
        },
        {
            'name': 'absol-mega',
            'url': 'https://pokeapi.co/api/v2/pokemon/10057/',
        },
        {
            'name': 'garchomp-mega',
            'url': 'https://pokeapi.co/api/v2/pokemon/10058/',
        },
        {
            'name': 'latias-mega',
            'url': 'https://pokeapi.co/api/v2/pokemon/10062/',
        },
        {
            'name': 'latios-mega',
            'url': 'https://pokeapi.co/api/v2/pokemon/10063/',
        },
        {
            'name': 'sceptile-mega',
            'url': 'https://pokeapi.co/api/v2/pokemon/10065/',
        },
        {
            'name': 'sableye-mega',
            'url': 'https://pokeapi.co/api/v2/pokemon/10066/',
        },
        {
            'name': 'gallade-mega',
            'url': 'https://pokeapi.co/api/v2/pokemon/10068/',
        },
        {
            'name': 'steelix-mega',
            'url': 'https://pokeapi.co/api/v2/pokemon/10072/',
        },
        {
            'name': 'metagross-mega',
            'url': 'https://pokeapi.co/api/v2/pokemon/10076/',
        },
        {
            'name': 'groudon-primal',
            'url': 'https://pokeapi.co/api/v2/pokemon/10078/',
        },
        {
            'name': 'lopunny-mega',
            'url': 'https://pokeapi.co/api/v2/pokemon/10088/',
        },
        {
            'name': 'salamence-mega',
            'url': 'https://pokeapi.co/api/v2/pokemon/10089/',
        },
        {
            'name': 'beedrill-mega',
            'url': 'https://pokeapi.co/api/v2/pokemon/10090/',
        },
    ],
    'machines': [
        {
            'machine': {'url': 'https://pokeapi.co/api/v2/machine/1578/'},
            'version_group': {
                'name': 'red-blue',
                'url': 'https://pokeapi.co/api/v2/version-group/1/',
            },
        },
        {
            'machine': {'url': 'https://pokeapi.co/api/v2/machine/1579/'},
            'version_group': {
                'name': 'yellow',
                'url': 'https://pokeapi.co/api/v2/version-group/2/',
            },
        },
        {
            'machine': {'url': 'https://pokeapi.co/api/v2/machine/1580/'},
            'version_group': {
                'name': 'gold-silver',
                'url': 'https://pokeapi.co/api/v2/version-group/3/',
            },
        },
        {
            'machine': {'url': 'https://pokeapi.co/api/v2/machine/1581/'},
            'version_group': {
                'name': 'crystal',
                'url': 'https://pokeapi.co/api/v2/version-group/4/',
            },
        },
        {
            'machine': {'url': 'https://pokeapi.co/api/v2/machine/1582/'},
            'version_group': {
                'name': 'ruby-sapphire',
                'url': 'https://pokeapi.co/api/v2/version-group/5/',
            },
        },
        {
            'machine': {'url': 'https://pokeapi.co/api/v2/machine/1583/'},
            'version_group': {
                'name': 'emerald',
                'url': 'https://pokeapi.co/api/v2/version-group/6/',
            },
        },
        {
            'machine': {'url': 'https://pokeapi.co/api/v2/machine/1584/'},
            'version_group': {
                'name': 'firered-leafgreen',
                'url': 'https://pokeapi.co/api/v2/version-group/7/',
            },
        },
        {
            'machine': {'url': 'https://pokeapi.co/api/v2/machine/1585/'},
            'version_group': {
                'name': 'diamond-pearl',
                'url': 'https://pokeapi.co/api/v2/version-group/8/',
            },
        },
        {
            'machine': {'url': 'https://pokeapi.co/api/v2/machine/1586/'},
            'version_group': {
                'name': 'platinum',
                'url': 'https://pokeapi.co/api/v2/version-group/9/',
            },
        },
        {
            'machine': {'url': 'https://pokeapi.co/api/v2/machine/1587/'},
            'version_group': {
                'name': 'heartgold-soulsilver',
                'url': 'https://pokeapi.co/api/v2/version-group/10/',
            },
        },
        {
            'machine': {'url': 'https://pokeapi.co/api/v2/machine/1588/'},
            'version_group': {
                'name': 'black-white',
                'url': 'https://pokeapi.co/api/v2/version-group/11/',
            },
        },
        {
            'machine': {'url': 'https://pokeapi.co/api/v2/machine/1589/'},
            'version_group': {
                'name': 'colosseum',
                'url': 'https://pokeapi.co/api/v2/version-group/12/',
            },
        },
        {
            'machine': {'url': 'https://pokeapi.co/api/v2/machine/1590/'},
            'version_group': {
                'name': 'xd',
                'url': 'https://pokeapi.co/api/v2/version-group/13/',
            },
        },
        {
            'machine': {'url': 'https://pokeapi.co/api/v2/machine/1591/'},
            'version_group': {
                'name': 'black-2-white-2',
                'url': 'https://pokeapi.co/api/v2/version-group/14/',
            },
        },
        {
            'machine': {'url': 'https://pokeapi.co/api/v2/machine/1592/'},
            'version_group': {
                'name': 'x-y',
                'url': 'https://pokeapi.co/api/v2/version-group/15/',
            },
        },
        {
            'machine': {'url': 'https://pokeapi.co/api/v2/machine/1593/'},
            'version_group': {
                'name': 'omega-ruby-alpha-sapphire',
                'url': 'https://pokeapi.co/api/v2/version-group/16/',
            },
        },
        {
            'machine': {'url': 'https://pokeapi.co/api/v2/machine/1595/'},
            'version_group': {
                'name': 'red-green-japan',
                'url': 'https://pokeapi.co/api/v2/version-group/28/',
            },
        },
        {
            'machine': {'url': 'https://pokeapi.co/api/v2/machine/1596/'},
            'version_group': {
                'name': 'blue-japan',
                'url': 'https://pokeapi.co/api/v2/version-group/29/',
            },
        },
        {
            'machine': {'url': 'https://pokeapi.co/api/v2/machine/1808/'},
            'version_group': {
                'name': 'brilliant-diamond-shining-pearl',
                'url': 'https://pokeapi.co/api/v2/version-group/23/',
            },
        },
    ],
    'meta': {
        'ailment': {
            'name': 'none',
            'url': 'https://pokeapi.co/api/v2/move-ailment/0/',
        },
        'ailment_chance': 0,
        'category': {
            'name': 'damage',
            'url': 'https://pokeapi.co/api/v2/move-category/0/',
        },
        'crit_rate': 0,
        'drain': 0,
        'flinch_chance': 0,
        'healing': 0,
        'max_hits': None,
        'max_turns': None,
        'min_hits': None,
        'min_turns': None,
        'stat_chance': 0,
    },
    'names': [
        {
            'language': {
                'name': 'ja-hrkt',
                'url': 'https://pokeapi.co/api/v2/language/1/',
            },
            'name': 'いあいぎり',
        },
        {
            'language': {
                'name': 'ko',
                'url': 'https://pokeapi.co/api/v2/language/3/',
            },
            'name': '풀베기',
        },
        {
            'language': {
                'name': 'zh-hant',
                'url': 'https://pokeapi.co/api/v2/language/4/',
            },
            'name': '居合斬',
        },
        {
            'language': {
                'name': 'fr',
                'url': 'https://pokeapi.co/api/v2/language/5/',
            },
            'name': 'Coupe',
        },
        {
            'language': {
                'name': 'de',
                'url': 'https://pokeapi.co/api/v2/language/6/',
            },
            'name': 'Zerschneider',
        },
        {
            'language': {
                'name': 'es',
                'url': 'https://pokeapi.co/api/v2/language/7/',
            },
            'name': 'Corte',
        },
        {
            'language': {
                'name': 'it',
                'url': 'https://pokeapi.co/api/v2/language/8/',
            },
            'name': 'Taglio',
        },
        {
            'language': {
                'name': 'en',
                'url': 'https://pokeapi.co/api/v2/language/9/',
            },
            'name': 'Cut',
        },
        {
            'language': {
                'name': 'ja',
                'url': 'https://pokeapi.co/api/v2/language/11/',
            },
            'name': 'いあいぎり',
        },
        {
            'language': {
                'name': 'zh-hans',
                'url': 'https://pokeapi.co/api/v2/language/12/',
            },
            'name': '居合斬',
        },
    ],
    'past_values': [],
    'power': 50,
    'pp': 30,
    'priority': 0,
    'stat_changes': [],
    'super_contest_effect': {'url': 'https://pokeapi.co/api/v2/super-contest-effect/5/'},
    'target': {
        'name': 'selected-pokemon',
        'url': 'https://pokeapi.co/api/v2/move-target/10/',
    },
    'type': {
        'name': 'normal',
        'url': 'https://pokeapi.co/api/v2/type/1/',
    },
}

MOCK_RESPONSE_BY_GROWTH_RATE_DATA = {
    'name': 'medium',
    'id': 2,
    'formula': 'x^3',
    'levels': [{'experience': 0, 'level': 1}, {'experience': 8, 'level': 2}],
    'descriptions': [
        {
            'description': 'moyenne',
            'language': {
                'name': 'fr',
                'url': 'https://pokeapi.co/api/v2/language/5/',
            },
        }
    ],
}

MOCK_RESPONSE_BY_EVOLUTION_ORDER_DATA = {
    'baby_trigger_item': None,
    'chain': {
        'evolution_details': [],
        'evolves_to': [
            {
                'evolution_details': [
                    {
                        'base_form_id': None,
                        'gender': None,
                        'held_item': None,
                        'item': None,
                        'known_move': None,
                        'known_move_type': None,
                        'location': None,
                        'min_affection': None,
                        'min_beauty': None,
                        'min_damage_taken': None,
                        'min_happiness': None,
                        'min_level': 16,
                        'min_move_count': None,
                        'min_steps': None,
                        'needs_multiplayer': False,
                        'needs_overworld_rain': False,
                        'party_species': None,
                        'party_type': None,
                        'region_id': None,
                        'relative_physical_stats': None,
                        'time_of_day': '',
                        'trade_species': None,
                        'trigger': {
                            'name': 'level-up',
                            'url': 'https://pokeapi.co/api/v2/evolution-trigger/1/',
                        },
                        'turn_upside_down': False,
                        'used_move': None,
                    }
                ],
                'evolves_to': [
                    {
                        'evolution_details': [
                            {
                                'base_form_id': None,
                                'gender': None,
                                'held_item': None,
                                'item': None,
                                'known_move': None,
                                'known_move_type': None,
                                'location': None,
                                'min_affection': None,
                                'min_beauty': None,
                                'min_damage_taken': None,
                                'min_happiness': None,
                                'min_level': 32,
                                'min_move_count': None,
                                'min_steps': None,
                                'needs_multiplayer': False,
                                'needs_overworld_rain': False,
                                'party_species': None,
                                'party_type': None,
                                'region_id': None,
                                'relative_physical_stats': None,
                                'time_of_day': '',
                                'trade_species': None,
                                'trigger': {
                                    'name': 'level-up',
                                    'url': 'https://pokeapi.co/api/v2/evolution-trigger/1/',
                                },
                                'turn_upside_down': False,
                                'used_move': None,
                            }
                        ],
                        'evolves_to': [],
                        'is_baby': False,
                        'species': {
                            'name': 'venusaur',
                            'url': 'https://pokeapi.co/api/v2/pokemon-species/3/',
                        },
                    }
                ],
                'is_baby': False,
                'species': {
                    'name': 'ivysaur',
                    'url': 'https://pokeapi.co/api/v2/pokemon-species/2/',
                },
            }
        ],
        'is_baby': False,
        'species': {
            'name': 'bulbasaur',
            'url': 'https://pokeapi.co/api/v2/pokemon-species/1/',
        },
    },
    'id': 1,
}
