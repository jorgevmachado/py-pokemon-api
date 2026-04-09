from sqlalchemy.orm import selectinload

from app.core.repository import BaseRepository
from app.models.captured_pokemon import CapturedPokemon
from app.models.pokedex import Pokedex
from app.models.pokemon import Pokemon
from app.models.pokemon_type import PokemonType
from app.models.trainer import Trainer


class TrainerRepository(BaseRepository[Trainer]):
    model = Trainer
    relations = (
        selectinload(Trainer.pokedex),
        selectinload(Trainer.pokedex)
        .selectinload(Pokedex.pokemon)
        .selectinload(Pokemon.moves),
        selectinload(Trainer.pokedex)
        .selectinload(Pokedex.pokemon)
        .selectinload(Pokemon.abilities),
        selectinload(Trainer.pokedex)
        .selectinload(Pokedex.pokemon)
        .selectinload(Pokemon.growth_rate),
        selectinload(Trainer.pokedex)
        .selectinload(Pokedex.pokemon)
        .selectinload(Pokemon.types)
        .selectinload(PokemonType.strengths),
        selectinload(Trainer.pokedex)
        .selectinload(Pokedex.pokemon)
        .selectinload(Pokemon.types)
        .selectinload(PokemonType.weaknesses),
        selectinload(Trainer.pokedex)
        .selectinload(Pokedex.pokemon)
        .selectinload(Pokemon.evolutions),
        selectinload(Trainer.captured_pokemons),
        selectinload(Trainer.captured_pokemons)
        .selectinload(CapturedPokemon.pokemon)
        .selectinload(Pokemon.moves),
        selectinload(Trainer.captured_pokemons)
        .selectinload(CapturedPokemon.pokemon)
        .selectinload(Pokemon.abilities),
        selectinload(Trainer.captured_pokemons)
        .selectinload(CapturedPokemon.pokemon)
        .selectinload(Pokemon.growth_rate),
        selectinload(Trainer.captured_pokemons)
        .selectinload(CapturedPokemon.pokemon)
        .selectinload(Pokemon.types)
        .selectinload(PokemonType.strengths),
        selectinload(Trainer.captured_pokemons)
        .selectinload(CapturedPokemon.pokemon)
        .selectinload(Pokemon.types)
        .selectinload(PokemonType.weaknesses),
        selectinload(Trainer.captured_pokemons)
        .selectinload(CapturedPokemon.pokemon)
        .selectinload(Pokemon.evolutions),
        selectinload(Trainer.captured_pokemons).selectinload(CapturedPokemon.moves),
    )
