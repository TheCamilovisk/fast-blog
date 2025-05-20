from http import HTTPStatus

from fastapi import FastAPI

from src.routers import auth, comments, posts, users
from src.schemas.message import MessageSchema

app = FastAPI()


@app.get('/', status_code=HTTPStatus.OK, response_model=MessageSchema)
async def get_root():
    return {'message': 'Welcome to Fast Blog!'}


app.include_router(users.router)
app.include_router(auth.router)
app.include_router(posts.router)
app.include_router(comments.router)
