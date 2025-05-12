from pydantic import BaseModel, Field


class MessageSchema(BaseModel):
    message: str = Field(examples='Operation completed successfully.')
