from datetime import datetime
from typing import TypedDict

from pydantic import BaseModel

class InitialPokemonTypeSchema(BaseModel):
    id: str
    url: str
    name: str
    order: int
    text_color: str
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None
    background_color: str

class PokemonTypeSchema(InitialPokemonTypeSchema):
    weaknesses: list[InitialPokemonTypeSchema]

class TypeColor(TypedDict):
    id: int
    name: str
    text_color: str
    background_color: str