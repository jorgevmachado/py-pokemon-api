from pydantic import BaseModel, ConfigDict


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
