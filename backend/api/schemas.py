from pydantic import BaseModel


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


class UserUpdateSchema(BaseModel):
    username: str | None = None
    password: str | None = None
    email: str | None = None


class UserSearchSchema(BaseModel):
    username: str | None = None
    email: str | None = None
