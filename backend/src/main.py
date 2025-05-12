from http import HTTPStatus

from fastapi import FastAPI

from src.schemas.message import MessageSchema

app = FastAPI()


@app.get('/', status_code=HTTPStatus.OK, response_model=MessageSchema)
async def get_root():
    return {'message': 'Welcome to Fast Blog!'}
