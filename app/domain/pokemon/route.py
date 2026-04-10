from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.pagination import CustomLimitOffsetPage
from app.core.security import get_current_user
from app.domain.pokemon.schema import PokemonFilterPage, PokemonSchema
from app.domain.pokemon.service import PokemonService
from app.models.trainer import Trainer

router = APIRouter(prefix='/pokemon', tags=['pokemon'])
Service = Annotated[PokemonService, Depends()]
CurrentTrainer = Annotated[Trainer, Depends(get_current_user)]


@router.get('/', response_model=CustomLimitOffsetPage[PokemonSchema] | list[PokemonSchema])
async def list_pokemons(
    service: Service,
    trainer: CurrentTrainer,
    page_filter: Annotated[PokemonFilterPage, Depends()],
):
    return await service.list_all_cached(page_filter=page_filter, user_request=trainer.name)


@router.get('/{pokemon_name}', response_model=PokemonSchema)
async def find_one_pokemon(
    pokemon_name: str,
    service: Service,
    trainer: CurrentTrainer,
):
    pokemon = await service.fetch_one_cached(name=pokemon_name, user_request=trainer.name)
    return PokemonSchema.model_validate(pokemon)
