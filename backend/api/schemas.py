from pydantic import BaseModel, ConfigDict


class MessageSchema(BaseModel):
    message: str


class UserSchema(BaseModel):
    username: str
    password: str
    email: str


class UserPublicSchema(BaseModel):
    id: int
    username: str
    email: str

    model_config = ConfigDict(from_attributes=True)


class UserUpdateSchema(BaseModel):
    username: str | None = None
    email: str | None = None


class TokenSchema(BaseModel):
    access_token: str
    token_type: str


class PaginationFilter(BaseModel):
    offset: int = 0
    limit: int = 10

    def __init__(self, **data):
        super().__init__(**data)
        self.offset = max(self.offset, 0)
        self.limit = max(self.limit, 1)


class TagPublicSchema(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class SearchPatternSchema(PaginationFilter):
    pattern: str | None = None


class TagsSearchResultSchema(BaseModel):
    search_params: SearchPatternSchema
    total_items: int
    tags: list[TagPublicSchema]

    model_config = ConfigDict(from_attributes=True)


class UserSearchSchema(PaginationFilter):
    username: str | None = None
    email: str | None = None


class UsersSearchResultSchema(BaseModel):
    search_params: UserSearchSchema
    total_items: int
    users: list[UserPublicSchema]

    model_config = ConfigDict(from_attributes=True)


class AuthorsSearchSchema(PaginationFilter):
    username: str | None = None
    firstname: str | None = None
    lastname: str | None = None


class AuthorListSchema(BaseModel):
    id: int
    username: str
    firstname: str
    lastname: str
    author_url: str


class AuthorsSearchResultSchema(BaseModel):
    search_params: AuthorsSearchSchema
    total_items: int
    authors: list[AuthorListSchema]


class AuthorPublicSchema(BaseModel):
    id: int
    user_id: int
    username: str
    firstname: str
    lastname: str
    email: str
    bio: str | None = None
    website: str | None = None


class AuthorCreateSchema(BaseModel):
    firstname: str
    lastname: str
    bio: str | None = None
    website: str | None = None


class AuthorUpdateSchema(BaseModel):
    firstname: str | None = None
    lastname: str | None = None
    bio: str | None = None
    website: str | None = None
