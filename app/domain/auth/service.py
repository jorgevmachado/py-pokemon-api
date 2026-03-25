import logging
from datetime import datetime
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.exceptions.exceptions import UnauthorizedException, handle_service_exception
from app.core.logging import LoggingParams, log_service_success
from app.core.security import create_access_token, verify_password
from app.domain.auth.schema import Token
from app.domain.trainer.service import TrainerService

Session = Annotated[AsyncSession, Depends(get_session)]
Service = Annotated[TrainerService, Depends()]
logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, service: Service):
        self.trainer_service = service
        self.logger_params = LoggingParams(logger=logger, service='auth', operation='')

    async def authenticate(self, email: str, password: str) -> Token | None:
        try:
            trainer = await self.trainer_service.find_one_by_email(email)

            if not trainer:
                raise UnauthorizedException

            trainer.total_authentications += 1

            if not verify_password(password, trainer.password):
                trainer.authentication_failures += 1
                await self.trainer_service.update(trainer)
                raise UnauthorizedException
            access_token = create_access_token({'sub': trainer.email})
            trainer.last_authentication_at = datetime.now()
            trainer.authentication_success += 1
            await self.trainer_service.update(trainer)

            log_service_success(
                self.logger_params, operation='authenticate', message='User authenticated'
            )
            return Token(access_token=access_token, token_type='bearer')

        except Exception as exception:
            handle_service_exception(
                exception,
                logger=self.logger_params.logger,
                service=self.logger_params.service,
                operation='authenticate',
            )
