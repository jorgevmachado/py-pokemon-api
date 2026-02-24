from pydantic import BaseModel, ConfigDict


class PokemonExternalBase(BaseModel):
    model_config = ConfigDict(extra='ignore')

    url: str
    name: str


class PokemonExternalLanguage(BaseModel):
    model_config = ConfigDict(extra='ignore')

    name: str
    url: str


class PokemonExternalBaseSchemaResponse(BaseModel):
    model_config = ConfigDict(extra='ignore')

    url: str
    order: int
    name: str
    external_image: str
