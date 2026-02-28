from pydantic import BaseModel

from app.domain.pokemon.external.schemas import (
    PokemonExternalBase,
    PokemonExternalTypeDamageRelationsSchemaResponse,
)


class TypeColor(BaseModel):
    id: int
    name: str
    text_color: str
    background_color: str


class TypeRelation(BaseModel):
    weakness: list[PokemonExternalBase] = []
    strengths: list[PokemonExternalBase] = []


class PokemonTypeBusiness:
    TYPE_COLORS = [
        TypeColor(id=1, name='ice', text_color='#fff', background_color='#51c4e7'),
        TypeColor(id=2, name='bug', text_color='#b5d7a7', background_color='#482d53'),
        TypeColor(id=3, name='fire', text_color='#fff', background_color='#fd7d24'),
        TypeColor(id=4, name='rock', text_color='#fff', background_color='#a38c21'),
        TypeColor(id=5, name='dark', text_color='#fff', background_color='#707070'),
        TypeColor(id=6, name='steel', text_color='#fff', background_color='#9eb7b8'),
        TypeColor(id=7, name='ghost', text_color='#fff', background_color='#7b62a3'),
        TypeColor(id=8, name='fairy', text_color='#cb3fa0', background_color='#c8a2c8'),
        TypeColor(id=9, name='water', text_color='#fff', background_color='#4592c4'),
        TypeColor(id=10, name='grass', text_color='#212121', background_color='#9bcc50'),
        TypeColor(id=11, name='normal', text_color='#000', background_color='#fff'),
        TypeColor(id=12, name='dragon', text_color='#fff', background_color='#FF8C00'),
        TypeColor(id=13, name='poison', text_color='#fff', background_color='#b97fc9'),
        TypeColor(id=14, name='flying', text_color='#424242', background_color='#3dc7ef'),
        TypeColor(id=15, name='ground', text_color='#f5f5f5', background_color='#bc5e00'),
        TypeColor(id=16, name='psychic', text_color='#fff', background_color='#f366b9'),
        TypeColor(id=17, name='electric', text_color='#212121', background_color='#eed535'),
        TypeColor(id=18, name='fighting', text_color='#fff', background_color='#d56723'),
    ]

    @staticmethod
    def ensure_colors(pokemon_type: str) -> TypeColor:
        default_type_color = TypeColor(
            id=0, name='default', text_color='#fff', background_color='#000'
        )
        type_color = next(
            (color for color in PokemonTypeBusiness.TYPE_COLORS if color.name == pokemon_type),
            default_type_color,
        )

        return type_color

    @staticmethod
    def ensure_damage_relations(
        damage_relations: PokemonExternalTypeDamageRelationsSchemaResponse,
    ) -> TypeRelation:
        weakness: set[str] = set()
        if damage_relations.double_damage_from:
            weakness.update(item.name for item in damage_relations.double_damage_from)

        if damage_relations.half_damage_from:
            weakness.update(item.name for item in damage_relations.half_damage_from)

        strengths: set[str] = set()
        if damage_relations.double_damage_to:
            strengths.update(item.name for item in damage_relations.double_damage_to)

        if damage_relations.half_damage_to:
            strengths.update(item.name for item in damage_relations.half_damage_to)

        weakness_items = (damage_relations.double_damage_from or []) + (
            damage_relations.half_damage_from or []
        )
        seen_weakness: set[str] = set()
        weakness_list = [
            item
            for item in weakness_items
            if item.name not in seen_weakness and not seen_weakness.add(item.name)
        ]

        strengths_items = (damage_relations.double_damage_to or []) + (
            damage_relations.half_damage_to or []
        )
        seen_strengths: set[str] = set()
        strengths_list = [
            item
            for item in strengths_items
            if item.name not in seen_strengths and not seen_strengths.add(item.name)
        ]

        return TypeRelation(weakness=weakness_list, strengths=strengths_list)
