from pydantic import BaseModel


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    type_type: str = 'bearer'


class TokenDataSchema(BaseModel):
    username: str | None = None


class RefreshTokenRequestSchema(BaseModel):
    refresh_token: str
