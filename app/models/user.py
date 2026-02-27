from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import UUID, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import default_lazy, table_registry
from app.shared.gender_enum import GenderEnum
from app.shared.role_enum import RoleEnum
from app.shared.status_enum import StatusEnum

if TYPE_CHECKING:
    from app.models.captured_pokemon import CapturedPokemon
    from app.models.pokedex import Pokedex


@table_registry.mapped_as_dataclass
class User:
    __tablename__ = 'users'

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, init=False, default=uuid4
    )
    role: Mapped[RoleEnum]
    name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    gender: Mapped[GenderEnum]
    status: Mapped[StatusEnum]
    password: Mapped[str]
    pokeballs: Mapped[int]
    capture_rate: Mapped[int]
    date_of_birth: Mapped[datetime]
    total_authentications: Mapped[int]
    authentication_success: Mapped[int]
    authentication_failures: Mapped[int]
    last_authentication_at: Mapped[datetime | None] = mapped_column(
        nullable=True, default=None
    )
    created_at: Mapped[datetime] = mapped_column(init=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), onupdate=func.now()
    )
    deleted_at: Mapped[datetime | None] = mapped_column(init=False, default=None)
    # FK
    pokedex: Mapped[list['Pokedex']] = relationship(
        init=False, lazy=default_lazy, back_populates='trainer'
    )
    # FK
    captured_pokemons: Mapped[list['CapturedPokemon']] = relationship(
        init=False, lazy=default_lazy, back_populates='trainer'
    )
