from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class PokemonTypeWeaknessSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    url: str
    name: str
    order: int
    text_color: str
    background_color: str


class PokemonTypeSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    url: str
    name: str
    order: int
    text_color: str
    background_color: str
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    weaknesses: list[PokemonTypeWeaknessSchema] = []


class InitialPokemonTypeSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    url: str
    name: str
    order: int
    text_color: str
    background_color: str


class CreatePokemonTypeSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    url: str
    name: str
    order: int
    text_color: str
    background_color: str
