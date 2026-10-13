from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CommentCreate(BaseModel):
    content: str = Field(min_length=1)


class CommentResponse(BaseModel):
    id: int
    ticket_id: int
    author_id: int
    content: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
    
class CommentUpdate(BaseModel):
    content: str = Field(min_length=1)