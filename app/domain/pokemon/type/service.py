from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.domain.pokemon.external.schema import PokemonTypeResponse
from app.domain.pokemon.type.repository import PokemonTypeRepository
from app.domain.pokemon.type.schema import PokemonTypeSchema, TypeColor
from app.models import Type
from app.shared.number import ensure_order_number

Session = Annotated[AsyncSession, Depends(get_session)]

class PokemonTypeService:
    def __init__(self, session: Session):
        self.session = session
        self.repository = PokemonTypeRepository(session)

    TYPE_COLORS: list[TypeColor] = [
        {'id': 1, 'name': 'ice', 'text_color': '#fff', 'background_color': '#51c4e7'},
        {'id': 2, 'name': 'bug', 'text_color': '#b5d7a7', 'background_color': '#482d53'},
        {'id': 3, 'name': 'fire', 'text_color': '#fff', 'background_color': '#fd7d24'},
        {'id': 4, 'name': 'rock', 'text_color': '#fff', 'background_color': '#a38c21'},
        {'id': 5, 'name': 'dark', 'text_color': '#fff', 'background_color': '#707070'},
        {'id': 6, 'name': 'steel', 'text_color': '#fff', 'background_color': '#9eb7b8'},
        {'id': 7, 'name': 'ghost', 'text_color': '#fff', 'background_color': '#7b62a3'},
        {'id': 8, 'name': 'fairy', 'text_color': '#cb3fa0', 'background_color': '#c8a2c8'},
        {'id': 9, 'name': 'water', 'text_color': '#fff', 'background_color': '#4592c4'},
        {'id': 10, 'name': 'grass', 'text_color': '#212121', 'background_color': '#9bcc50'},
        {'id': 11, 'name': 'normal', 'text_color': '#000', 'background_color': '#fff'},
        {'id': 12, 'name': 'dragon', 'text_color': '#fff', 'background_color': '#FF8C00'},
        {'id': 13, 'name': 'poison', 'text_color': '#fff', 'background_color': '#b97fc9'},
        {'id': 14, 'name': 'flying', 'text_color': '#424242', 'background_color': '#3dc7ef'},
        {'id': 15, 'name': 'ground', 'text_color': '#f5f5f5', 'background_color': '#bc5e00'},
        {'id': 16, 'name': 'psychic', 'text_color': '#fff', 'background_color': '#f366b9'},
        {'id': 17, 'name': 'electric', 'text_color': '#212121', 'background_color': '#eed535'},
        {'id': 18, 'name': 'fighting', 'text_color': '#fff', 'background_color': '#d56723'},
    ]

    async def convert_types_to_pokemon_types(self, types: list[PokemonTypeResponse])-> list[PokemonTypeSchema]:
        result = []
        for type_response in types:
            url = type_response.type.url
            name = type_response.type.name
            order = ensure_order_number(url)

            pokemon_type = await self.repository.find_one_by_order(order)
            if pokemon_type:
                result.append(pokemon_type)
                continue

            type_color = next(
                (color for color in self.TYPE_COLORS if color['name'] == name),
                {'text_color': '#FFF', 'background_color': '#000'}
            )

            pokemon_type = await self.repository.create(
                order=order,
                name=name,
                url=url,
                text_color=type_color['text_color'],
                background_color=type_color['background_color']
            )

            result.append(pokemon_type)
        return result







