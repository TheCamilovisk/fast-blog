from datetime import datetime

from pydantic import BaseModel, Field

from src.schemas.pagination import PaginationSchema


class CreatePostRequestSchema(BaseModel):
    title: str = Field(..., examples=['My first post'])
    subtitle: str = Field(..., examples=['An intro to blogging'])
    content: str = Field(
        ..., examples=['This is the full content of the post']
    )


class UpdatePostRequestSchema(BaseModel):
    title: str | None = Field(None, examples=['My first post'])
    subtitle: str | None = Field(None, examples=['An intro to blogging'])
    content: str | None = Field(
        None, examples=['This is the full content of the post']
    )


class PostResponseSchema(BaseModel):
    id: int
    title: str
    subtitle: str | None
    slug: str
    content: str
    is_published: bool
    created_at: datetime
    updated_at: datetime
    published_at: datetime | None
    author_id: int

    class Config:
        from_attributes = True


class PostListResponseSchema(BaseModel):
    pagination: PaginationSchema
    posts: list[PostResponseSchema]
