from http import HTTPStatus

from fastapi import FastAPI

from api.routers import auth, tags, users
from api.schemas import MessageSchema

app = FastAPI()


@app.get('/', status_code=HTTPStatus.OK, response_model=MessageSchema)
def get_root():
    return {'message': 'Hello World!!!'}


app.include_router(users.router)
app.include_router(auth.router)
app.include_router(tags.router)
