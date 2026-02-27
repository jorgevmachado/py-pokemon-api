from typing import Annotated

from fastapi import Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_session
from app.domain.pokedex.schema import CreatePokedexSchema
from app.models import Pokedex, User
from app.shared.schemas import FilterPage

Session = Annotated[AsyncSession, Depends(get_session)]


class PokedexRepository:
    def __init__(self, session: Session):
        self.session = session

    async def create(self, create_pokedex: CreatePokedexSchema) -> Pokedex:
        pokedex = Pokedex(
            hp=create_pokedex.hp,
            wins=create_pokedex.wins,
            level=create_pokedex.level,
            iv_hp=create_pokedex.iv_hp,
            ev_hp=create_pokedex.ev_hp,
            losses=create_pokedex.losses,
            max_hp=create_pokedex.max_hp,
            battles=create_pokedex.battles,
            nickname=create_pokedex.nickname,
            iv_speed=create_pokedex.iv_speed,
            ev_speed=create_pokedex.ev_speed,
            iv_attack=create_pokedex.iv_attack,
            ev_attack=create_pokedex.ev_attack,
            iv_defense=create_pokedex.iv_defense,
            ev_defense=create_pokedex.ev_defense,
            experience=create_pokedex.experience,
            iv_special_attack=create_pokedex.iv_special_attack,
            ev_special_attack=create_pokedex.ev_special_attack,
            iv_special_defense=create_pokedex.iv_special_defense,
            ev_special_defense=create_pokedex.ev_special_defense,
            discovered=create_pokedex.discovered,
            pokemon_id=create_pokedex.pokemon_id,
            trainer_id=create_pokedex.trainer_id,
        )
        if create_pokedex.discovered_at is not None:
            pokedex.discovered_at = create_pokedex.discovered_at

        self.session.add(pokedex)
        await self.session.commit()
        await self.session.refresh(pokedex)
        return pokedex

    async def find_by_trainer(
        self,
        trainer_id: str,
    ) -> set[str]:
        """Find all pokemon_ids that exist in pokedex for a trainer."""
        query = select(Pokedex.pokemon_id).where(
            Pokedex.trainer_id == trainer_id,
            Pokedex.trainer_id.isnot(None),  # Ignore bad legacy data with NULL
        )
        result = await self.session.scalars(query)
        # Return a set of string IDs (no objects, no tracking)
        return set(result.all())

    async def find_by_trainer_and_pokemon(
        self,
        trainer_id: str,
        pokemon_id: str,
    ) -> Pokedex | None:
        """Find pokedex entry by trainer and pokemon."""
        query = select(Pokedex).where(
            Pokedex.trainer_id == trainer_id,
            Pokedex.pokemon_id == pokemon_id,
        )
        result = await self.session.scalar(query)
        return result

    async def list(
        self, user: User, pokedex_filter: Annotated[FilterPage, Query()] = FilterPage()
    ):
        query = select(Pokedex).options(
            selectinload(Pokedex.trainer),
            selectinload(Pokedex.pokemon),
        )

        pokedex = await self.session.scalars(
            query
            .offset(pokedex_filter.offset)
            .limit(pokedex_filter.limit)
            .where(Pokedex.trainer_id == user.id)
        )
        return pokedex.all()
