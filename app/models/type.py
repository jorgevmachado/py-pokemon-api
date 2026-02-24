from datetime import datetime
from uuid import uuid4

from sqlalchemy import UUID, ForeignKey, func
from sqlalchemy.orm import Mapped, Relationship, mapped_column

from app.models.base import default_lazy, table_registry


@table_registry.mapped_as_dataclass
class TypeWeaknessFK:
    __tablename__ = 'type_weaknesses'
    type_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey('types.id'), primary_key=True
    )
    weakness_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey('types.id'), primary_key=True
    )


@table_registry.mapped_as_dataclass
class PokemonType:
    __tablename__ = 'types'

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, init=False, default=uuid4
    )
    url: Mapped[str]
    name: Mapped[str] = mapped_column(unique=True)
    order: Mapped[int]
    text_color: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), onupdate=func.now()
    )
    deleted_at: Mapped[datetime] = mapped_column(init=False, nullable=True)
    background_color: Mapped[str]

    # FK
    weaknesses: Mapped[list['PokemonType']] = Relationship(
        lazy=default_lazy,
        secondary='type_weaknesses',
        primaryjoin='PokemonType.id == type_weaknesses.c.type_id',
        secondaryjoin='PokemonType.id == type_weaknesses.c.weakness_id',
    )
