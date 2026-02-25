from pydantic import BaseModel, ConfigDict


class CreatePokemonGrowthRateSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    url: str
    name: str
    order: int
    formula: str
    description: str
