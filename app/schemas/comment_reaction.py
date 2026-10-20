from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.models.models import ReactionType


class CommentReactionCreate(BaseModel):
    reaction_type: ReactionType


class CommentReactionResponse(BaseModel):
    id: int
    comment_id: int
    user_id: int
    reaction_type: ReactionType
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CommentReactionsListResponse(BaseModel):
    comment_id: int
    total_reactions: int
    thumbs_up_count: int
    thumbs_down_count: int
    reactions: list[CommentReactionResponse]
