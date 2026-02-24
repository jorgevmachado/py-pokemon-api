from datetime import datetime
from uuid import uuid4

from sqlalchemy import UUID, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import table_registry


@table_registry.mapped_as_dataclass
class PokemonGrowthRate:
    __tablename__ = 'growth_rates'

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, init=False, default=uuid4
    )
    url: Mapped[str]
    name: Mapped[str] = mapped_column(unique=True)
    order: Mapped[int]
    formula: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(init=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), onupdate=func.now()
    )
    deleted_at: Mapped[datetime] = mapped_column(init=False, nullable=True)
