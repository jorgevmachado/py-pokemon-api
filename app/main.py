from http import HTTPStatus

from fastapi import FastAPI

from app.domain import auth, user, pokemon
from app.shared.schemas import Message

app = FastAPI()

app.include_router(user.router)
app.include_router(auth.router)
app.include_router(pokemon.router)


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {'message': 'Hello World!'}
