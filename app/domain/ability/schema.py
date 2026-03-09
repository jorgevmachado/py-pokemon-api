from pydantic import BaseModel, ConfigDict


class CreatePokemonAbilitySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    url: str
    name: str
    order: int
    slot: int
    is_hidden: bool
