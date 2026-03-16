from app.domain.pokemon.model import Pokemon
from app.shared.enums.status_enum import StatusEnum

MOCK_ENTITY_ORDER = 1

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
