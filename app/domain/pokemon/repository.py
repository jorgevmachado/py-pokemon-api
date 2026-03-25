from sqlalchemy.orm import selectinload

from app.core.repository import BaseRepository
from app.domain.type.model import PokemonType
from app.models.pokemon import Pokemon


class PokemonRepository(BaseRepository[Pokemon]):
    model = Pokemon
    default_order_by = 'order'
    relations = (
        selectinload(Pokemon.growth_rate),
        selectinload(Pokemon.moves),
        selectinload(Pokemon.types).selectinload(PokemonType.weaknesses),
        selectinload(Pokemon.types).selectinload(PokemonType.strengths),
        selectinload(Pokemon.abilities),
        selectinload(Pokemon.evolutions)
        .selectinload(Pokemon.types)
        .selectinload(PokemonType.weaknesses)
        .selectinload(PokemonType.strengths),
        selectinload(Pokemon.evolutions).selectinload(Pokemon.growth_rate),
    )
