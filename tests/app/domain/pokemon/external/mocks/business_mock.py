from app.domain.pokemon.external.business.business import (
    EnsureAttributesSchemaResult,
    EnsureSpecieAttributesSchemaResult,
)

MOCK_ATTRIBUTES_HP = 45
MOCK_ATTRIBUTES_SPEED = 45
MOCK_ATTRIBUTES_ATTACK = 49
MOCK_ATTRIBUTES_SPECIAL_ATTACK = 65
MOCK_ATTRIBUTES_DEFENSE = 65
MOCK_ATTRIBUTES_SPECIAL_DEFENSE = 65
MOCK_ATTRIBUTES_HEIGHT = 7
MOCK_ATTRIBUTES_WEIGHT = 69
MOCK_ATTRIBUTES_BASE_EXPERIENCE = 64
MOCK_EXTERNAL_API_URL = 'https://pokeapi.co/api/v2'

MOCK_BUSINESS_ENSURE_ATTRIBUTES = EnsureAttributesSchemaResult(
    hp=MOCK_ATTRIBUTES_HP,
    speed=MOCK_ATTRIBUTES_SPEED,
    attack=MOCK_ATTRIBUTES_ATTACK,
    defense=MOCK_ATTRIBUTES_DEFENSE,
    special_attack=MOCK_ATTRIBUTES_SPECIAL_ATTACK,
    special_defense=MOCK_ATTRIBUTES_SPECIAL_DEFENSE,
    height=MOCK_ATTRIBUTES_HEIGHT,
    weight=MOCK_ATTRIBUTES_WEIGHT,
    base_experience=MOCK_ATTRIBUTES_BASE_EXPERIENCE,
)

MOCK_BUSINESS_SPECIE_ENSURE_ATTRIBUTES = EnsureSpecieAttributesSchemaResult(
    habitat='grassland',
    is_baby=False,
    shape_name='quadruped',
    shape_url='https://pokeapi.co/api/v2/pokemon-shape/8/',
    is_mythical=False,
    gender_rate=1,
    is_legendary=False,
    capture_rate=45,
    hatch_counter=20,
    base_happiness=70,
    evolution_chain_url='https://pokeapi.co/api/v2/evolution-chain/1/',
    evolves_from_species=None,
    has_gender_differences=False,
)
