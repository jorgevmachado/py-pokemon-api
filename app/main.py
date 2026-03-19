from http import HTTPStatus

from fastapi import FastAPI
from fastapi_pagination import add_pagination

from app.core.logging import configure_logging, logging_middleware
from app.domain.auth.route import router as auth_router
from app.domain.battle.route import router as battle_router
from app.domain.captured_pokemon.route import router as captured_pokemon_router
from app.domain.pokedex.route import router as pokedex_router
from app.domain.pokemon.route import router as pokemon_router
from app.domain.trainer.route import router as trainer_router
from app.shared.schemas import Message

configure_logging()

app = FastAPI()

app.middleware('http')(logging_middleware)

app.include_router(trainer_router)
app.include_router(auth_router)
app.include_router(pokemon_router)
app.include_router(pokedex_router)
app.include_router(captured_pokemon_router)
app.include_router(battle_router)

add_pagination(app)


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {'message': 'Hello World!'}
