from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_session
from app.domain.user.schema import CreateUserSchema, FindOneUserSchemaParams
from app.models import User
from app.shared.role_enum import RoleEnum
from app.shared.status_enum import StatusEnum

Session = Annotated[AsyncSession, Depends(get_session)]


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    async def create(self, create_user: CreateUserSchema) -> User:
        user = User(
            role=RoleEnum.USER,
            name=create_user.name,
            email=create_user.email,
            gender=create_user.gender,
            status=StatusEnum.ACTIVE,
            password=create_user.password,
            pokeballs=create_user.pokeballs,
            capture_rate=create_user.capture_rate,
            date_of_birth=create_user.date_of_birth,
            total_authentications=0,
            authentication_success=0,
            authentication_failures=0,
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update(self, user: User) -> User:
        await self.session.merge(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def find_one(self, params: FindOneUserSchemaParams) -> User | None:
        query = select(User).options(
            selectinload(User.pokedex), selectinload(User.captured_pokemons)
        )

        if params.id:
            return await self.session.scalar(query.where(User.id == params.id))
        if params.email:
            return await self.session.scalar(query.where(User.email == params.email))
        return None
