from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.models import User
from app.dependencies.auth import get_current_user

from app.schemas.comment_reaction import (
    CommentReactionCreate,
    CommentReactionResponse,
    CommentReactionsListResponse
)

from app.services import comment_reaction_service


router = APIRouter(
    prefix="/comments",
    tags=["Comment Reactions"]
)


@router.post(
    "/{comment_id}/reactions",
    response_model=CommentReactionResponse,
    status_code=200
)
def add_or_update_reaction(
    comment_id: int,
    reaction_data: CommentReactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    reaction, error = (
        comment_reaction_service.create_or_update_reaction(
            db=db,
            comment_id=comment_id,
            reaction_data=reaction_data,
            current_user=current_user
        )
    )

    if error == "comment_not_found":
        raise HTTPException(
            status_code=404,
            detail="Comment not found"
        )

    if error == "permission_denied":
        raise HTTPException(
            status_code=403,
            detail="You cannot react to this comment"
        )

    if error == "ticket_closed":
        raise HTTPException(
            status_code=400,
            detail="Cannot react to comments on a closed ticket"
        )

    return reaction


@router.get(
    "/{comment_id}/reactions",
    response_model=CommentReactionsListResponse
)
def get_reactions(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result, error = comment_reaction_service.get_comment_reactions(
        db=db,
        comment_id=comment_id,
        current_user=current_user
    )

    if error == "comment_not_found":
        raise HTTPException(
            status_code=404,
            detail="Comment not found"
        )

    if error == "permission_denied":
        raise HTTPException(
            status_code=403,
            detail="You cannot view reactions on this comment"
        )

    return result


@router.delete(
    "/{comment_id}/reactions",
    status_code=204
)
def remove_reaction(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    error = comment_reaction_service.delete_reaction(
        db=db,
        comment_id=comment_id,
        current_user=current_user
    )

    if error == "comment_not_found":
        raise HTTPException(
            status_code=404,
            detail="Comment not found"
        )

    if error == "permission_denied":
        raise HTTPException(
            status_code=403,
            detail="You cannot remove reactions on this comment"
        )

    if error == "ticket_closed":
        raise HTTPException(
            status_code=400,
            detail="Cannot remove reactions on a closed ticket"
        )

    if error == "reaction_not_found":
        raise HTTPException(
            status_code=404,
            detail="You have not reacted to this comment"
        )

    return None
