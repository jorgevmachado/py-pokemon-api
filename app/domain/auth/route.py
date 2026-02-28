from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.security import create_access_token, get_current_user
from app.domain.auth.schema import Login, Token
from app.domain.auth.service import AuthService
from app.domain.trainer.model import Trainer

router = APIRouter(prefix='/auth', tags=['auth'])
Session = Annotated[AsyncSession, Depends(get_session)]
OAUTH2Form = Annotated[OAuth2PasswordRequestForm, Depends()]
CurrentTrainer = Annotated[Trainer, Depends(get_current_user)]


@router.post('/token', response_model=Token)
async def login_for_access_token(
    form_data: Login,
    session: Session,
):
    service = AuthService(session)
    return await service.authenticate(form_data.email, form_data.password)


@router.post('/refresh_token', response_model=Token)
async def refresh_access_token(user: CurrentTrainer):
    new_access_token = create_access_token(data={'sub': user.email})

    return {'access_token': new_access_token, 'token_type': 'bearer'}
