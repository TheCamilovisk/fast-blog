from pydantic import BaseModel


class PaginationSchema(BaseModel):
    offset: int = 0
    limit: int = 10
