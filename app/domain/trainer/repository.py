from sqlalchemy.orm import selectinload

from app.domain.trainer.model import Trainer
from app.shared.base_repository import BaseRepository


class TrainerRepository(BaseRepository[Trainer]):
    model = Trainer
    relations = (selectinload(Trainer.pokedex), selectinload(Trainer.captured_pokemons))
