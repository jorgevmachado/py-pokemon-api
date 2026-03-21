from datetime import datetime

from app.domain.pokemon.schema import PokemonEvolutionSchema, PublicPokemonSchema

# Constants for test values (avoid magic numbers)
HP = 45
SPEED = 45
HEIGHT = 7
WEIGHT = 69
ATTACK = 49
DEFENSE = 49
GENDER_RATE = 1
HABITAT = 'grassland'


def test_pokemon_evolution_schema_fields():
    data = {
        'id': '1',
        'url': 'https://pokeapi.co/api/v2/pokemon/1/',
        'name': 'bulbasaur',
        'order': 1,
        'status': 'COMPLETE',
        'external_image': 'https://img.pokemondb.net/artwork/bulbasaur.jpg',
        'image': None,
        'types': [],
    }
    schema = PokemonEvolutionSchema(**data)
    assert schema.id == '1'
    assert schema.url == data['url']
    assert schema.name == 'bulbasaur'
    assert schema.order == 1
    assert schema.status == 'COMPLETE'
    assert schema.external_image == data['external_image']
    assert schema.image is None
    assert schema.types == []


def test_public_pokemon_schema_fields():
    dt = datetime(2024, 1, 1, 12, 0, 0)
    data = {
        'id': '1',
        'url': 'https://pokeapi.co/api/v2/pokemon/1/',
        'name': 'bulbasaur',
        'order': 1,
        'status': 'COMPLETE',
        'external_image': 'https://img.pokemondb.net/artwork/bulbasaur.jpg',
        'hp': HP,
        'image': None,
        'speed': SPEED,
        'height': HEIGHT,
        'weight': WEIGHT,
        'attack': ATTACK,
        'defense': DEFENSE,
        'habitat': HABITAT,
        'is_baby': False,
        'shape_url': None,
        'shape_name': None,
        'is_mythical': False,
        'gender_rate': GENDER_RATE,
        'is_legendary': False,
        'created_at': dt,
        'updated_at': dt,
    }
    schema = PublicPokemonSchema(**data)
    assert schema.id == '1'
    assert schema.url == data['url']
    assert schema.name == 'bulbasaur'
    assert schema.order == 1
    assert schema.status == 'COMPLETE'
    assert schema.external_image == data['external_image']
    assert schema.hp == HP
    assert schema.image is None
    assert schema.speed == SPEED
    assert schema.height == HEIGHT
    assert schema.weight == WEIGHT
    assert schema.attack == ATTACK
    assert schema.defense == DEFENSE
    assert schema.habitat == HABITAT
    assert schema.is_baby is False
    assert schema.shape_url is None
    assert schema.shape_name is None
    assert schema.is_mythical is False
    assert schema.gender_rate == GENDER_RATE
    assert schema.is_legendary is False
