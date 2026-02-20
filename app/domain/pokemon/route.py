from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.domain.pokemon.schema import PokemonPublicListSchema, PokemonPublicSchema
from app.domain.pokemon.service import PokemonService
from app.models import User
from app.security import get_current_user
from app.shared.schemas import FilterPage

Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]
router = APIRouter(prefix='/pokemon', tags=['pokemon'])

limit = 1302
@router.get('/', response_model=PokemonPublicListSchema)
async def list_pokemon(
        session: Session,
        pokemon_filter: Annotated[FilterPage, Query()]
):
    service = PokemonService(session)
    pokemons = await service.validate_database(pokemon_filter)
    return {'results': pokemons}

@router.get('/{name}', response_model=PokemonPublicSchema)
async def get_pokemon(name: str,session: Session):
    service = PokemonService(session)
    pokemon = await service.find_one(name)
    return pokemon