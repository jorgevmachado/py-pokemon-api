from http import HTTPStatus

from fastapi import FastAPI
from fastapi_pagination import add_pagination

from app.domain import auth, pokemon
from app.domain.trainer.route import router as trainer_router
from app.shared.schemas import Message

app = FastAPI()

app.include_router(trainer_router)
app.include_router(auth.router)
app.include_router(pokemon.router)

add_pagination(app)


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {'message': 'Hello World!'}
