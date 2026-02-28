from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.domain.captured_pokemon.model import CapturedPokemon
from app.domain.captured_pokemon.schema import CreateCapturedPokemonSchema

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
