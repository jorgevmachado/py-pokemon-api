from pydantic import BaseModel, ConfigDict


class PokemonAbilitySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    url: str
    name: str
    order: int
    slot: int
    is_hidden: bool


class CreatePokemonAbilitySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    url: str
    name: str
    order: int
    slot: int
    is_hidden: bool
