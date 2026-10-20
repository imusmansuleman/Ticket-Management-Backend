from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import datetime


class CommentCreate(BaseModel):
    content: str = Field(min_length=1)

    @field_validator("content")
    @classmethod
    def validate_content(cls, value: str):
        value = value.strip()

        if not value:
            raise ValueError("Comment cannot be empty")

        return value


class CommentUpdate(CommentCreate):
    pass


class CommentResponse(BaseModel):
    id: int
    ticket_id: int
    author_id: int
    content: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)