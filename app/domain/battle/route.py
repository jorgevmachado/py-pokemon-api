from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.domain.battle.schema import BattlePokemonSchema, BattleResult
from app.domain.battle.service import PokemonBattleService
from app.models.trainer import Trainer

router = APIRouter(prefix='/battle', tags=['battle'])
Service = Annotated[PokemonBattleService, Depends()]
CurrentTrainer = Annotated[Trainer, Depends(get_current_user)]


@router.post(
    '/',
    response_model=BattleResult,
)
async def battle(
    service: Service, trainer: CurrentTrainer, battle_pokemon: BattlePokemonSchema
):
    return await service.battle(trainer=trainer, battle_pokemon=battle_pokemon)
