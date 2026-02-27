from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.domain.user.schema import (
    CreateUserSchema,
    UserInitializeTrainerSchema,
    UserPublicSchema,
)
from app.domain.user.service import UserService
from app.models import User
from app.security import get_current_user

router = APIRouter(prefix='/users', tags=['users'])
Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/', status_code=HTTPStatus.CREATED, response_model=UserPublicSchema)
async def create_user(user: CreateUserSchema, session: Session):
    service = UserService(session)
    return await service.create(user)


@router.post('/initialize', response_model=UserPublicSchema)
async def initialize(
    session: Session, params: UserInitializeTrainerSchema, current_user: CurrentUser
):
    service = UserService(session)
    return await service.initialize(params, current_user)


@router.get('/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublicSchema)
async def get_user(user_id: str, session: Session, current_user: CurrentUser):
    service = UserService(session)
    return await service.find_one(user_id, current_user)
