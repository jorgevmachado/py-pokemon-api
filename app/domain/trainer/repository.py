from sqlalchemy.orm import selectinload

from app.core.repository import BaseRepository
from app.domain.trainer.model import Trainer


class TrainerRepository(BaseRepository[Trainer]):
    model = Trainer
    relations = (selectinload(Trainer.pokedex), selectinload(Trainer.captured_pokemons))
