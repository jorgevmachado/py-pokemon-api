from datetime import datetime
from http import HTTPStatus
from typing import Annotated

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.security import create_access_token, verify_password
from app.domain.trainer.service import TrainerService

Session = Annotated[AsyncSession, Depends(get_session)]
Service = Annotated[TrainerService, Depends()]


class AuthService:
    def __init__(self, service: Service):
        self.trainer_service = service

    async def authenticate(self, email: str, password: str):
        error_message = 'Incorrect email or password'
        try:
            trainer = await self.trainer_service.find_one_by_email(email)

            if not trainer:
                raise HTTPException(
                    detail=error_message,
                    status_code=HTTPStatus.UNAUTHORIZED,
                )

            trainer.total_authentications += 1

            if not verify_password(password, trainer.password):
                trainer.authentication_failures += 1
                await self.trainer_service.update(trainer)
                raise HTTPException(
                    detail=error_message,
                    status_code=HTTPStatus.UNAUTHORIZED,
                )

            access_token = create_access_token({'sub': trainer.email})
            trainer.last_authentication_at = datetime.now()
            trainer.authentication_success += 1
            await self.trainer_service.update(trainer)
            return {'access_token': access_token, 'token_type': 'bearer'}
        except Exception as e:
            print(f'# => auth  service => authenticate => error => {e}')
            raise HTTPException(
                detail=error_message,
                status_code=HTTPStatus.UNAUTHORIZED,
            )
