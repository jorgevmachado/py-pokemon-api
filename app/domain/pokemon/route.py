from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.security import get_current_user
from app.domain.pokemon.schema import PokemonListSchema, PokemonSchema
from app.domain.pokemon.service import PokemonService
from app.domain.trainer.model import Trainer
from app.shared.schemas import FilterPage

router = APIRouter(prefix='/pokemon', tags=['pokemon'])
Session = Annotated[AsyncSession, Depends(get_session)]
CurrentTrainer = Annotated[Trainer, Depends(get_current_user)]


@router.get('/', response_model=PokemonListSchema)
async def list_pokemons(
    session: Session,
    trainer: CurrentTrainer,
    pokemon_filter: Annotated[FilterPage, Query()],
):
    service = PokemonService(session)
    pokemons = await service.fetch_all(pokemon_filter=pokemon_filter)
    # Convert ORM objects to Pydantic schemas to avoid lazy-loading issues
    results = [PokemonSchema.model_validate(pokemon) for pokemon in pokemons]
    return {'results': results}


@router.get('/{pokemon_name}', response_model=PokemonSchema)
async def find_one_pokemon(
    pokemon_name: str,
    session: Session,
    trainer: CurrentTrainer,
):
    service = PokemonService(session)
    pokemon = await service.fetch_one(name=pokemon_name)
    # Convert ORM to Pydantic schema to avoid lazy-loading issues
    return PokemonSchema.model_validate(pokemon)
