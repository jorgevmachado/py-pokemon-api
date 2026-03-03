from datetime import datetime
from uuid import uuid4

from sqlalchemy import UUID, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base import default_lazy, table_registry
from app.domain.move.model import PokemonMove
from app.domain.pokemon.model import Pokemon
from app.domain.trainer.model import Trainer


@table_registry.mapped_as_dataclass
class CapturedPokemonMoveFK:
    __tablename__ = 'captured_pokemon_moves'
    captured_pokemon_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey('captured_pokemons.id'), primary_key=True
    )
    move_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey('moves.id'), primary_key=True
    )


@table_registry.mapped_as_dataclass
class CapturedPokemon:
    __tablename__ = 'captured_pokemons'

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, init=False, default=uuid4
    )
    hp: Mapped[int]
    wins: Mapped[int]
    level: Mapped[int]
    iv_hp: Mapped[int]
    ev_hp: Mapped[int]
    losses: Mapped[int]
    max_hp: Mapped[int]
    battles: Mapped[int]
    nickname: Mapped[str]
    iv_speed: Mapped[int]
    ev_speed: Mapped[int]
    iv_attack: Mapped[int]
    ev_attack: Mapped[int]
    iv_defense: Mapped[int]
    ev_defense: Mapped[int]
    experience: Mapped[int]
    iv_special_attack: Mapped[int]
    ev_special_attack: Mapped[int]
    iv_special_defense: Mapped[int]
    ev_special_defense: Mapped[int]
    captured_at: Mapped[datetime]
    created_at: Mapped[datetime] = mapped_column(init=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), onupdate=func.now()
    )
    deleted_at: Mapped[datetime] = mapped_column(init=False, nullable=True)
    pokemon_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey('pokemon.id'))
    trainer_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey('trainers.id'))

    pokemon: Mapped['Pokemon'] = relationship(
        lazy=default_lazy,
        init=False,
    )

    trainer: Mapped['Trainer'] = relationship(
        lazy=default_lazy, init=False, back_populates='captured_pokemons'
    )

    moves: Mapped[list['PokemonMove']] = relationship(
        lazy=default_lazy, secondary='captured_pokemon_moves', init=False, default_factory=list
    )
