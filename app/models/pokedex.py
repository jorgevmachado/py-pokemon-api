from datetime import datetime
from uuid import uuid4

from sqlalchemy import UUID, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import default_lazy, table_registry
from app.models.pokemon import Pokemon
from app.models.user import User


@table_registry.mapped_as_dataclass
class Pokedex:
    __tablename__ = 'pokedex'

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
    discovered: Mapped[bool]
    discovered_at: Mapped[datetime] = mapped_column(init=False, nullable=True)
    created_at: Mapped[datetime] = mapped_column(init=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), onupdate=func.now()
    )
    deleted_at: Mapped[datetime] = mapped_column(init=False, nullable=True)

    pokemon_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey('pokemon.id'))
    trainer_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey('users.id'))

    pokemon: Mapped['Pokemon'] = relationship(
        lazy=default_lazy,
        init=False,
    )

    trainer: Mapped['User'] = relationship(
        lazy=default_lazy, init=False, back_populates='pokedex'
    )
