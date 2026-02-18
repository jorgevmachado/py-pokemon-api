from uuid import uuid4
from datetime import datetime
from sqlalchemy import UUID, func,ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, Relationship

from app.models import GrowthRate, Move, Type, Ability
from app.models.base import table_registry, default_lazy
from app.shared.status_enum import StatusEnum

@table_registry.mapped_as_dataclass
class PokemonMoveFK:
    __tablename__ = 'pokemon_moves'

    pokemon_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey('pokemon.id'), primary_key=True)
    move_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey('moves.id'), primary_key=True)

@table_registry.mapped_as_dataclass
class PokemonAbilityFK:
    __tablename__ = 'pokemon_abilities'

    pokemon_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey('pokemon.id'), primary_key=True)
    ability_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey('abilities.id'), primary_key=True)

@table_registry.mapped_as_dataclass
class PokemonTypeFK:
    __tablename__ = 'pokemon_types'
    pokemon_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey('pokemon.id'), primary_key=True)
    type_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey('types.id'), primary_key=True)

@table_registry.mapped_as_dataclass
class PokemonEvolutionFK:
    __tablename__ = 'pokemon_evolutions'
    pokemon_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey('pokemon.id'), primary_key=True)
    evolution_id: Mapped[str] = mapped_column(UUID(as_uuid=False),ForeignKey('pokemon.id'), primary_key=True)

@table_registry.mapped_as_dataclass
class Pokemon:
    __tablename__ = 'pokemon'

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, init=False, default=uuid4)
    hp: Mapped[int] = mapped_column(nullable=True)
    url: Mapped[str]
    name: Mapped[str] = mapped_column(unique=True)
    order: Mapped[int]
    image: Mapped[str] = mapped_column(nullable=True)
    speed: Mapped[int] = mapped_column(nullable=True)
    status: Mapped[StatusEnum]
    height: Mapped[int] = mapped_column(nullable=True)
    weight: Mapped[int] = mapped_column(nullable=True)
    attack: Mapped[int] = mapped_column(nullable=True)
    defense: Mapped[int] = mapped_column(nullable=True)
    habitat: Mapped[str] = mapped_column(nullable=True)
    is_baby: Mapped[bool] = mapped_column(nullable=True)
    shape_url: Mapped[str] = mapped_column(nullable=True)
    shape_name: Mapped[str] = mapped_column(nullable=True)
    is_mythical: Mapped[bool] = mapped_column(nullable=True)
    gender_rate: Mapped[int] = mapped_column(nullable=True)
    is_legendary: Mapped[bool] = mapped_column(nullable=True)
    capture_rate: Mapped[int] = mapped_column(nullable=True)
    hatch_counter: Mapped[int] = mapped_column(nullable=True)
    base_happiness: Mapped[int] = mapped_column(nullable=True)
    special_attack: Mapped[int] = mapped_column(nullable=True)
    external_image: Mapped[str]
    base_experience: Mapped[int] = mapped_column(nullable=True)
    special_defense: Mapped[int] = mapped_column(nullable=True)
    evolution_chain_url: Mapped[str] = mapped_column(nullable=True)
    evolves_from_species: Mapped[str] = mapped_column(nullable=True)
    has_gender_differences: Mapped[bool] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), onupdate=func.now()
    )
    deleted_at: Mapped[datetime] = mapped_column(init=False, nullable=True)
    # FK
    growth_rate_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey('growth_rates.id'))
    growth_rate: Mapped['GrowthRate'] = Relationship(
        lazy=default_lazy,
    )
    # FK
    moves: Mapped[list['Move']] = Relationship(
        lazy=default_lazy,
        secondary='pokemon_moves'
    )
    # FK
    types: Mapped[list['Type']] = Relationship(
        lazy=default_lazy,
        secondary='pokemon_types'
    )
    # FK
    abilities: Mapped[list['Ability']] = Relationship(
        lazy=default_lazy,
        secondary='pokemon_abilities'
    )
    # FK
    evolutions: Mapped[list['Pokemon']] = Relationship(
        lazy=default_lazy,
        secondary='pokemon_evolutions',
        primaryjoin='Pokemon.id == pokemon_evolutions.c.pokemon_id',
        secondaryjoin='Pokemon.id == pokemon_evolutions.c.evolution_id',
    )