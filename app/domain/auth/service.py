from datetime import datetime
from http import HTTPStatus
from typing import Annotated

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.domain.user.service import UserService
from app.security import create_access_token, verify_password

Session = Annotated[AsyncSession, Depends(get_session)]


class AuthService:
    def __init__(self, session: Session):
        self.user_service = UserService(session)

    async def authenticate(self, email: str, password: str):
        error_message = 'Incorrect email or password'
        try:
            user = await self.user_service.find_one_by_email(email)

            if not user:
                raise HTTPException(
                    detail=error_message,
                    status_code=HTTPStatus.UNAUTHORIZED,
                )
            user.authentication_failures += user.total_authentications

            if not verify_password(password, user.password):
                user.authentication_failures += user.authentication_failures
                await self.user_service.update(user)
                raise HTTPException(
                    detail=error_message,
                    status_code=HTTPStatus.UNAUTHORIZED,
                )

            access_token = create_access_token({'sub': user.email})
            user.last_authentication_at = datetime.now()
            user.authentication_success += user.authentication_success
            await self.user_service.update(user)
            return {'access_token': access_token, 'token_type': 'bearer'}
        except Exception as e:
            print(f'# => auth  service => authenticate => error => {e}')
            raise HTTPException(
                detail=error_message,
                status_code=HTTPStatus.UNAUTHORIZED,
            )
