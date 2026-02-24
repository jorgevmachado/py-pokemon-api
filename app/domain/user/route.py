from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.domain.user.schema import UserCreateSchema, UserPublicSchema
from app.models import User
from app.security import get_current_user, get_password_hash
from app.shared.role_enum import RoleEnum
from app.shared.status_enum import StatusEnum

router = APIRouter(prefix='/users', tags=['users'])
Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/', status_code=HTTPStatus.CREATED, response_model=UserPublicSchema)
async def create_user(user: UserCreateSchema, session: Session):
    db_user = await session.scalar(select(User).where(User.email == user.email))

    if db_user and db_user.email == user.email:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Email already exists',
        )

    db_user = User(
        role=RoleEnum.USER,
        name=user.name,
        email=user.email,
        gender=user.gender,
        status=StatusEnum.ACTIVE,
        password=get_password_hash(user.password),
        pokeballs=5,
        capture_rate=45,
        date_of_birth=user.date_of_birth,
        total_authentications=0,
        authentication_success=0,
        authentication_failures=0,
    )
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user


@router.get(
    '/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublicSchema
)
async def get_user(user_id: str, session: Session, current_user: CurrentUser):
    db_user = await session.scalar(select(User).where(User.id == user_id))

    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions'
        )
    return db_user
