from datetime import datetime

from pydantic import BaseModel, Field

from src.schemas.pagination import PaginationSchema


class CreateCommentRequestSchema(BaseModel):
    post_id: int = Field(..., examples=[1])
    content: str = Field(..., examples=['Create post!'])
    parent_id: int | None = Field(None, examples=[5])


class UpdateCommentRequestSchema(BaseModel):
    content: str | None = Field(None, examples=['Create post!'])


class CommentResponseSchema(BaseModel):
    id: int
    content: str
    author_id: int
    post_id: int
    parent_id: int | None
    created_at: datetime
    replies: list['CommentResponseSchema'] = []

    class Config:
        from_attributes = True


class CommentListResponseSchema(BaseModel):
    pagination: PaginationSchema
    comments: list[CommentResponseSchema]
