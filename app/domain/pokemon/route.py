from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi_pagination import LimitOffsetPage
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.security import get_current_user
from app.domain.pokemon.schema import PokemonSchema
from app.domain.pokemon.service import PokemonService
from app.domain.trainer.model import Trainer
from app.shared.schemas import FilterPage

router = APIRouter(prefix='/pokemon', tags=['pokemon'])
Session = Annotated[AsyncSession, Depends(get_session)]
CurrentTrainer = Annotated[Trainer, Depends(get_current_user)]


@router.get('/', response_model=LimitOffsetPage[PokemonSchema] | list[PokemonSchema])
async def list_pokemons(
    session: Session,
    trainer: CurrentTrainer,
    page_filter: Annotated[FilterPage, Depends()],
):
    service = PokemonService(session)
    return await service.fetch_all(page_filter=page_filter)


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
