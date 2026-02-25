from pydantic import BaseModel, ConfigDict


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
