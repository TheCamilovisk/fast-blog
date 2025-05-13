from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.schemas.user import CreateUserRequest, UserResponse
from src.services.user_service import UserService

router = APIRouter(prefix='/users', tags=['users'])

DBSession = Annotated[AsyncSession, Depends(get_session)]


@router.post('/', status_code=HTTPStatus.CREATED)
async def create_user(
    user_data: CreateUserRequest, session: DBSession
) -> UserResponse:
    "Create a new user. Raises 409 if the email or username is already taken."
    try:
        user = await UserService.create_user(session, user_data)
    except ValueError as e:
        raise HTTPException(status_code=HTTPStatus.CONFLICT, detail=str(e))
    return user
