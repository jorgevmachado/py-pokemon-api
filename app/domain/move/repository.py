from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.domain.move.model import PokemonMove
from app.domain.move.schema import CreatePokemonMoveSchema

Session = Annotated[AsyncSession, Depends(get_session)]


class PokemonMoveRepository:
    def __init__(self, session: Session):
        self.session = session

    async def create(self, create_pokemon_move: CreatePokemonMoveSchema) -> PokemonMove:
        pokemon_move = PokemonMove(
            pp=create_pokemon_move.pp,
            url=create_pokemon_move.url,
            type=create_pokemon_move.type,
            name=create_pokemon_move.name,
            order=create_pokemon_move.order,
            power=create_pokemon_move.power,
            target=create_pokemon_move.target,
            effect=create_pokemon_move.effect,
            priority=create_pokemon_move.priority,
            accuracy=create_pokemon_move.accuracy,
            short_effect=create_pokemon_move.short_effect,
            damage_class=create_pokemon_move.damage_class,
            effect_chance=create_pokemon_move.effect_chance,
        )
        self.session.add(pokemon_move)
        await self.session.commit()
        await self.session.refresh(pokemon_move)
        return pokemon_move

    async def find_one_by_order(self, order: int) -> PokemonMove:
        return await self.session.scalar(select(PokemonMove).where(PokemonMove.order == order))
