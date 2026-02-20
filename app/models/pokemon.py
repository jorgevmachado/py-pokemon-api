from datetime import datetime
from uuid import uuid4

from sqlalchemy import UUID, ForeignKey, func, Integer, String, Boolean
from sqlalchemy.orm import Mapped, relationship, mapped_column

from app.models.ability import Ability
from app.models.base import default_lazy, table_registry
from app.models.growth_rate import GrowthRate
from app.models.move import Move
from app.models.type import Type
from app.shared.status_enum import StatusEnum


@table_registry.mapped_as_dataclass
class PokemonMoveFK:
    __tablename__ = 'pokemon_moves'

    pokemon_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey('pokemon.id'), primary_key=True
    )
    move_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey('moves.id'), primary_key=True
    )


@table_registry.mapped_as_dataclass
class PokemonAbilityFK:
    __tablename__ = 'pokemon_abilities'

    pokemon_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey('pokemon.id'), primary_key=True
    )
    ability_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey('abilities.id'), primary_key=True
    )


@table_registry.mapped_as_dataclass
class PokemonTypeFK:
    __tablename__ = 'pokemon_types'
    pokemon_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey('pokemon.id'), primary_key=True
    )
    type_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey('types.id'), primary_key=True
    )


@table_registry.mapped_as_dataclass
class PokemonEvolutionFK:
    __tablename__ = 'pokemon_evolutions'
    pokemon_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey('pokemon.id'), primary_key=True
    )
    evolution_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey('pokemon.id'), primary_key=True
    )


@table_registry.mapped_as_dataclass
class Pokemon:
    __tablename__ = 'pokemon'

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        init=False,
        default=uuid4
    )
    name: Mapped[str] = mapped_column(unique=True)
    url: Mapped[str]
    order: Mapped[int]
    status: Mapped[StatusEnum]
    external_image: Mapped[str]

    hp: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    image: Mapped[str] = mapped_column(String, nullable=True, default=None)
    speed: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    height: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    weight: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    attack: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    defense: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    habitat: Mapped[str] = mapped_column(String, nullable=True, default=None)
    is_baby: Mapped[bool] = mapped_column(Boolean, nullable=True, default=None)
    shape_url: Mapped[str] = mapped_column(String, nullable=True, default=None)
    shape_name: Mapped[str] = mapped_column(String, nullable=True, default=None)
    is_mythical: Mapped[bool] = mapped_column(Boolean, nullable=True, default=None)
    gender_rate: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    is_legendary: Mapped[bool] = mapped_column(Boolean, nullable=True, default=None)
    capture_rate: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    hatch_counter: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    base_happiness: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    special_attack: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    base_experience: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    special_defense: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    evolution_chain_url: Mapped[str] = mapped_column(String, nullable=True, default=None)
    evolves_from_species: Mapped[str] = mapped_column(String, nullable=True, default=None)
    has_gender_differences: Mapped[bool] = mapped_column(Boolean, nullable=True, default=None)
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), onupdate=func.now()
    )
    deleted_at: Mapped[datetime] = mapped_column(init=False, nullable=True)
    # FK
    growth_rate_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey('growth_rates.id'),
        nullable=True,
        default=None
    )
    growth_rate: Mapped['GrowthRate'] = relationship(
        lazy=default_lazy,
        init=False,
        default=None
    )
    # FK
    moves: Mapped[list['Move']] = relationship(
        lazy=default_lazy,
        secondary='pokemon_moves',
        init=False,
        default_factory=list
    )
    # FK
    types: Mapped[list['Type']] = relationship(
        lazy=default_lazy,
        secondary='pokemon_types',
        init=False,
        default_factory=list
    )
    # FK
    abilities: Mapped[list['Ability']] = relationship(
        lazy=default_lazy,
        secondary='pokemon_abilities',
        init=False,
        default_factory=list
    )
    # FK
    evolutions: Mapped[list['Pokemon']] = relationship(
        lazy=default_lazy,
        secondary='pokemon_evolutions',
        primaryjoin='Pokemon.id == pokemon_evolutions.c.pokemon_id',
        secondaryjoin='Pokemon.id == pokemon_evolutions.c.evolution_id',
        init=False,
        default_factory=list
    )
