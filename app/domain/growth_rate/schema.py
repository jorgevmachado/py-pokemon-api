from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class PokemonGrowthRateSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    url: str
    name: str
    order: int
    formula: str
    description: str
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None


class CreatePokemonGrowthRateSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    url: str
    name: str
    order: int
    formula: str
    description: str
