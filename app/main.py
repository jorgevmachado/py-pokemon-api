from fastapi import FastAPI
from http import HTTPStatus

from app.domain import user, auth
from app.shared.schemas import Message

app = FastAPI()

app.include_router(user.router)
app.include_router(auth.router)
@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return { 'message': 'Hello World!'}