from http import HTTPStatus

from fastapi import APIRouter, HTTPException

from src.core.dependencies import DBSession
from src.schemas.user import CreateUserRequestSchema, UserResponseSchema
from src.services.user_service import UserService

router = APIRouter(prefix='/users', tags=['users'])


@router.post('/', status_code=HTTPStatus.CREATED)
async def create_user(
    user_data: CreateUserRequestSchema, session: DBSession
) -> UserResponseSchema:
    "Create a new user. Raises 409 if the email or username is already taken."
    try:
        user = await UserService.create_user(session, user_data)
    except ValueError as e:
        raise HTTPException(status_code=HTTPStatus.CONFLICT, detail=str(e))
    return user
