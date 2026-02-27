from http import HTTPStatus
from typing import Annotated

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.domain.user.repository import UserRepository
from app.domain.user.schema import CreateUserSchema, FindOneUserSchemaParams
from app.models import User

Session = Annotated[AsyncSession, Depends(get_session)]


class UserService:
    def __init__(self, session: Session):
        self.repository = UserRepository(session)

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
