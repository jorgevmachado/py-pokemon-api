from http import HTTPStatus
from typing import Annotated

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.domain.captured_pokemon.service import CapturedPokemonService
from app.domain.pokedex.service import PokedexService
from app.domain.pokemon.service import PokemonService
from app.domain.user.repository import UserRepository
from app.domain.user.schema import (
    CreateUserSchema,
    FindOneUserSchemaParams,
    UserInitializeTrainerSchema,
)
from app.models import User
from app.shared.status_enum import StatusEnum

Session = Annotated[AsyncSession, Depends(get_session)]


class UserService:
    def __init__(self, session: Session):
        self.repository = UserRepository(session)
        self.pokemon_service = PokemonService(session)
        self.pokedex_service = PokedexService(session)
        self.captured_pokemon_service = CapturedPokemonService(session)

    async def create(self, user: CreateUserSchema) -> User:
        db_user = await self.repository.find_one(
            params=FindOneUserSchemaParams(email=user.email)
        )

        if db_user and db_user.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Email already exists',
            )

        return await self.repository.create(user)

    async def find_one(self, user_id: str, user: User) -> User:
        db_user = await self.repository.find_one(params=FindOneUserSchemaParams(id=user_id))

        if not db_user:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='User not found')

        if user.id != user_id:
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions'
            )

        return db_user

    async def initialize(self, params: UserInitializeTrainerSchema, current_user: User):
        try:
            db_user = await self.find_one(user_id=current_user.id, user=current_user)

            if db_user.status == StatusEnum.INCOMPLETE:
                first_pokemon = await self.pokemon_service.first_pokemon(params.pokemon_name)

                if not first_pokemon:
                    raise HTTPException(
                        status_code=HTTPStatus.BAD_REQUEST,
                        detail='Not enough permissions to initialize',
                    )

                if not db_user.pokedex:
                    await self.pokedex_service.initialize(
                        user=current_user,
                        pokemon=first_pokemon.pokemon,
                        pokemons=first_pokemon.pokemons,
                    )

                if not db_user.captured_pokemons:
                    await self.captured_pokemon_service.create(
                        user=current_user,
                        pokemon=first_pokemon.pokemon,
                    )
                if not db_user.pokedex and not db_user.captured_pokemons:
                    db_user.status = StatusEnum.ACTIVE
                return await self.repository.update(user=db_user)

            return db_user
        except Exception as e:
            print(f'# => UserService => initialize => error => {e}')
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                detail='Error initializing trainer',
            )
