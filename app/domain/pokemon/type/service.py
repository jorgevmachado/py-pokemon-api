from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.domain.pokemon.external.schemas import PokemonExternalBaseTypeSchemaResponse
from app.domain.pokemon.type.business import PokemonTypeBusiness
from app.domain.pokemon.type.repository import PokemonTypeRepository
from app.domain.pokemon.type.schema import CreatePokemonTypeSchema
from app.models import PokemonType
from app.shared.number import ensure_order_number

Session = Annotated[AsyncSession, Depends(get_session)]


class PokemonTypeService:
    def __init__(self, session: Session):
        self.repository = PokemonTypeRepository(session)

    async def verify_pokemon_type(
        self, types: list[PokemonExternalBaseTypeSchemaResponse]
    ) -> list[PokemonType]:
        result_pokemon_type = []

        for type_response in types:
            url = type_response.type.url
            name = type_response.type.name
            order = ensure_order_number(url)

            db_pokemon_type = await self.repository.find_one_by_order(order=order)
            if db_pokemon_type:
                result_pokemon_type.append(db_pokemon_type)
                continue

            type_colors = PokemonTypeBusiness().ensure_colors(type_response)
            pokemon_type_data = CreatePokemonTypeSchema(
                url=url,
                name=name,
                order=order,
                text_color=type_colors.text_color,
                background_color=type_colors.background_color,
            )
            pokemon_type = await self.repository.create(pokemon_type_data)
            result_pokemon_type.append(pokemon_type)

        return result_pokemon_type
