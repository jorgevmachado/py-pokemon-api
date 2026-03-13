from app.domain.move.model import PokemonMove
from app.shared.base_repository import BaseRepository


class PokemonMoveRepository(BaseRepository[PokemonMove]):
    model = PokemonMove
    default_order_by = 'order'
