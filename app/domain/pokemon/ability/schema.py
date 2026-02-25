from pydantic import BaseModel


class CreatePokemonAbilitySchema(BaseModel):
    url: str
    name: str
    order: int
    slot: int
    is_hidden: bool
