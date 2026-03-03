from typing import Annotated

from fastapi import Depends, Query
from fastapi_pagination import LimitOffsetParams
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_session
from app.domain.captured_pokemon.model import CapturedPokemon
from app.domain.captured_pokemon.schema import (
    CapturedPokemonFilterPage,
    CreateCapturedPokemonSchema,
    FindCapturePokemonSchema,
)
from app.domain.pokemon.model import Pokemon
from app.shared.pagination import is_paginate, limit_paginate

Session = Annotated[AsyncSession, Depends(get_session)]


class CapturedPokemonRepository:
    def __init__(self, session: Session):
        self.session = session

    async def create(
        self, create_captured_pokemon: CreateCapturedPokemonSchema
    ) -> CapturedPokemon:
        captured_pokemon = CapturedPokemon(
            hp=create_captured_pokemon.hp,
            wins=create_captured_pokemon.wins,
            level=create_captured_pokemon.level,
            iv_hp=create_captured_pokemon.iv_hp,
            ev_hp=create_captured_pokemon.ev_hp,
            losses=create_captured_pokemon.losses,
            max_hp=create_captured_pokemon.max_hp,
            battles=create_captured_pokemon.battles,
            nickname=create_captured_pokemon.nickname,
            iv_speed=create_captured_pokemon.iv_speed,
            ev_speed=create_captured_pokemon.ev_speed,
            iv_attack=create_captured_pokemon.iv_attack,
            ev_attack=create_captured_pokemon.ev_attack,
            iv_defense=create_captured_pokemon.iv_defense,
            ev_defense=create_captured_pokemon.ev_defense,
            experience=create_captured_pokemon.experience,
            ev_special_attack=create_captured_pokemon.ev_special_attack,
            iv_special_attack=create_captured_pokemon.iv_special_attack,
            iv_special_defense=create_captured_pokemon.iv_special_defense,
            ev_special_defense=create_captured_pokemon.ev_special_defense,
            captured_at=create_captured_pokemon.captured_at,
            pokemon_id=create_captured_pokemon.pokemon_id,
            trainer_id=create_captured_pokemon.trainer_id,
        )
        self.session.add(captured_pokemon)
        await self.session.commit()
        await self.session.refresh(captured_pokemon)
        return captured_pokemon

    async def list_all(self, page_filter: Annotated[CapturedPokemonFilterPage, Query()]):
        trainer_id = page_filter.trainer_id
        query = (
            select(CapturedPokemon)
            .options(
                selectinload(CapturedPokemon.pokemon),
                selectinload(CapturedPokemon.pokemon).selectinload(Pokemon.moves),
                selectinload(CapturedPokemon.moves),
            )
            .order_by(CapturedPokemon.captured_at.desc())
            .where(CapturedPokemon.trainer_id == trainer_id)
        )

        if page_filter.nickname is not None:
            query = query.where(CapturedPokemon.nickname.ilike(f'%{page_filter.nickname}%'))

        if is_paginate(page_filter):
            params = LimitOffsetParams(
                limit=limit_paginate(page_filter.limit),
                offset=page_filter.offset,
            )
            return await paginate(self.session, query, params=params)
        captured_pokemons = await self.session.scalars(query)
        return captured_pokemons.all()

    async def find_by_pokemon(self, find_capture_pokemon: FindCapturePokemonSchema):
        if (
            find_capture_pokemon.pokemon_id is None
            and find_capture_pokemon.name is None
            and find_capture_pokemon.nickname is None
        ):
            return None

        query = (
            select(CapturedPokemon)
            .options(selectinload(CapturedPokemon.pokemon))
            .where(CapturedPokemon.trainer_id == find_capture_pokemon.trainer_id)
        )

        if find_capture_pokemon.pokemon_id is not None:
            query = query.where(CapturedPokemon.pokemon_id == find_capture_pokemon.pokemon_id)

        if find_capture_pokemon.name is not None:
            query = query.where(CapturedPokemon.pokemon.has(name=find_capture_pokemon.name))

        if find_capture_pokemon.nickname is not None:
            query = query.where(
                CapturedPokemon.nickname.ilike(f'%{find_capture_pokemon.nickname}%')
            )

        return await self.session.scalar(query)
