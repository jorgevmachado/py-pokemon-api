from pydantic import BaseModel, ConfigDict

from app.domain.pokemon.external.schemas import PokemonExternalLanguage


class PokemonExternalGrowthRateLevelSchemaResponse(BaseModel):
    model_config = ConfigDict(extra='ignore')
    level: int
    experience: int


class PokemonExternalGrowthRateDescriptionSchemaResponse(BaseModel):
    model_config = ConfigDict(extra='ignore')
    description: str
    language: PokemonExternalLanguage


class PokemonExternalGrowthRateSchemaResponse(BaseModel):
    model_config = ConfigDict(extra='ignore')
    id: int
    name: str
    formula: str
    levels: list[PokemonExternalGrowthRateLevelSchemaResponse]
    descriptions: list[PokemonExternalGrowthRateDescriptionSchemaResponse]
