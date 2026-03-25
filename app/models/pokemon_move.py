from datetime import datetime
from uuid import uuid4

from sqlalchemy import UUID, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import table_registry


@table_registry.mapped_as_dataclass
class PokemonMove:
    __tablename__ = 'moves'

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, init=False, default=uuid4
    )
    pp: Mapped[int]
    url: Mapped[str]
    type: Mapped[str]
    name: Mapped[str] = mapped_column(unique=True)
    order: Mapped[int]
    power: Mapped[int]
    target: Mapped[str]
    effect: Mapped[str]
    priority: Mapped[int]
    accuracy: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(init=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), onupdate=func.now()
    )
    deleted_at: Mapped[datetime] = mapped_column(init=False, nullable=True)
    short_effect: Mapped[str]
    damage_class: Mapped[str]
    effect_chance: Mapped[int] = mapped_column(nullable=True)
