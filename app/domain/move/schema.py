from pydantic import BaseModel, ConfigDict


class PokemonMoveSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    pp: int
    url: str
    type: str
    name: str
    order: int
    power: int
    target: str
    effect: str
    priority: int
    accuracy: int
    short_effect: str
    damage_class: str
    effect_chance: int | None = None


class CreatePokemonMoveSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    pp: int
    url: str
    type: str
    name: str
    order: int
    power: int
    target: str
    effect: str
    priority: int
    accuracy: int
    short_effect: str
    damage_class: str
    effect_chance: int | None = None
