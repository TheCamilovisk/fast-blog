from pydantic import BaseModel, EmailStr, Field


class CreateUserRequest(BaseModel):
    username: str = Field(
        ..., min_length=3, max_length=50, examples=['johndoe']
    )
    email: EmailStr = Field(..., examples=['user@example.com'])
    password: str = Field(
        ...,
        min_length=8,
        examples=['Str0ngP@ssw0rd'],
        description='Plain-text password, will be hashed befre storage.',
    )


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool
    is_superuser: bool

    class Config:
        from_attributes = True
