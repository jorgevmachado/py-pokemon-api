from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi_pagination import LimitOffsetPage

from app.core.security import get_current_user
from app.domain.pokemon.schema import PokemonSchema
from app.domain.pokemon.service import PokemonService
from app.domain.trainer.model import Trainer
from app.shared.schemas import FilterPage

router = APIRouter(prefix='/pokemon', tags=['pokemon'])
Service = Annotated[PokemonService, Depends()]
CurrentTrainer = Annotated[Trainer, Depends(get_current_user)]


@router.get('/', response_model=LimitOffsetPage[PokemonSchema] | list[PokemonSchema])
async def list_pokemons(
    service: Service,
    trainer: CurrentTrainer,
    page_filter: Annotated[FilterPage, Depends()],
):
    return await service.fetch_all(page_filter=page_filter)


@router.get('/{pokemon_name}', response_model=PokemonSchema)
async def find_one_pokemon(
    pokemon_name: str,
    service: Service,
    trainer: CurrentTrainer,
):
    pokemon = await service.fetch_one(name=pokemon_name)
    # Convert ORM to Pydantic schema to avoid lazy-loading issues
    return PokemonSchema.model_validate(pokemon)
