from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.domain.pokemon.schema import PokemonListSchema, PokemonSchema
from app.domain.pokemon.service import PokemonService
from app.models import User
from app.security import get_current_user
from app.shared.schemas import FilterPage

router = APIRouter(prefix='/pokemon', tags=['pokemon'])
Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.get('/', response_model=PokemonListSchema)
async def list_pokemons(
    session: Session,
    user: CurrentUser,
    pokemon_filter: Annotated[FilterPage, Query()],
):
    service = PokemonService(session)
    pokemons = await service.fetch_all(pokemon_filter=pokemon_filter)
    return {'results': pokemons}

@router.get('/{pokemon_name}', response_model=PokemonSchema)
async def find_one_pokemon(
    pokemon_name: str,
    session: Session,
    user: CurrentUser,
):
    service = PokemonService(session)
    pokemon = await service.fetch_one(name=pokemon_name)
    return pokemon