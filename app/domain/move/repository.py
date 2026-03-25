from app.core.repository import BaseRepository
from app.domain.move.model import PokemonMove


class PokemonMoveRepository(BaseRepository[PokemonMove]):
    model = PokemonMove
    default_order_by = 'order'
