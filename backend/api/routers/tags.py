from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from api.database import get_session
from api.repositories.tag_repository import TagRepository
from api.schemas import SearchPatternSchema, TagsSearchResultSchema

router = APIRouter(prefix='/tags', tags=['tags'])


DBSession = Annotated[Session, Depends(get_session)]

QueryParams = Annotated[SearchPatternSchema, Query()]


@router.get(
    '/', status_code=HTTPStatus.OK, response_model=TagsSearchResultSchema
)
async def list_tags(
    session: DBSession,
    params: QueryParams,
):
    tags = await TagRepository.list_all(
        session,
        pattern=params.pattern,
        limit=params.limit,
        offset=params.offset,
    )

    return {
        'search_params': params,
        'total_items': len(tags),
        'tags': tags,
    }
