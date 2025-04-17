from http import HTTPStatus

from fastapi import FastAPI

from api.routers import auth, authors, posts, tags, users
from api.schemas import MessageSchema

app = FastAPI()


@app.get('/', status_code=HTTPStatus.OK, response_model=MessageSchema)
async def get_root():
    return {'message': 'Hello World!!!'}


app.include_router(users.router)
app.include_router(auth.router)
app.include_router(tags.router)
app.include_router(authors.router)
app.include_router(posts.router)
