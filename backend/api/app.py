from http import HTTPStatus

from fastapi import FastAPI

from api.routers import users

app = FastAPI()


@app.get('/', status_code=HTTPStatus.OK)
def get_root():
    return {'message': 'Hello World!!!'}


app.include_router(users.router)
