from app.core.repository import BaseRepository
from app.models.pokemon_move import PokemonMove


class PokemonMoveRepository(BaseRepository[PokemonMove]):
    model = PokemonMove
    default_order_by = 'order'
