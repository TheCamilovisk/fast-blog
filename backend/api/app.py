from http import HTTPStatus

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.core.schemas import MessageSchema
from api.core.settings import get_settings
from api.routers import auth, authors, posts, tags, users

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().ORIGINS,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.get('/', status_code=HTTPStatus.OK, response_model=MessageSchema)
async def get_root():
    return {'message': 'Hello World!!!'}


app.include_router(users.router)
app.include_router(auth.router)
app.include_router(tags.router)
app.include_router(authors.router)
app.include_router(posts.router)
