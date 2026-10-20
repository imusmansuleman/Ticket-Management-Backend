from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import User
from app.dependencies.auth import get_current_user
from app.schemas.comment import (
    CommentCreate,
    CommentResponse,
    CommentUpdate
)
from app.services import comment_service


router = APIRouter(
    prefix="/tickets",
    tags=["Comments"]
)

my_comments_router = APIRouter(
    prefix="/comments",
    tags=["Comments"]
)


@router.post(
    "/{ticket_id}/comments",
    response_model=CommentResponse,
    status_code=201
)
def add_comment(
    ticket_id: int,
    comment_data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    comment, error = comment_service.create_comment(
        db=db,
        ticket_id=ticket_id,
        comment_data=comment_data,
        current_user=current_user
    )

    if error == "ticket_not_found":
        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    if error == "ticket_closed":
        raise HTTPException(
            status_code=400,
            detail="Cannot comment on a closed ticket"
        )

    if error == "permission_denied":
        raise HTTPException(
            status_code=403,
            detail="You cannot comment on this ticket"
        )

    return comment

# VIEWING COMMENTS ON YOUR TICKET BY ADMIN, ENG, EMP 
@router.get(
    "/{ticket_id}/comments",
    response_model=list[CommentResponse]
)
def get_comments(
    ticket_id: int,
    mine: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    comments, error = comment_service.get_ticket_comments(
        db=db,
        ticket_id=ticket_id,
        current_user=current_user,
        mine=mine
    )

    if error == "ticket_not_found":
        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    if error == "permission_denied":
        raise HTTPException(
            status_code=403,
            detail="You cannot view comments on this ticket"
        )

    return comments

# To UPDATE COMMENT
@router.patch(
    "/comments/{comment_id}",
    response_model=CommentResponse
)
def edit_comment(
    comment_id: int,
    comment_data: CommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    comment, error = comment_service.update_comment(
        db=db,
        comment_id=comment_id,
        comment_data=comment_data,
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
            detail="You cannot edit this comment"
        )

    if error == "ticket_closed":
        raise HTTPException(
            status_code=400,
            detail="Cannot edit comments on a closed ticket"
        )

    return comment

# TO DELETE COMMENT
@router.delete(
    "/comments/{comment_id}",
    status_code=204
)
def remove_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    error = comment_service.delete_comment(
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
            detail="You cannot delete this comment"
        )

    if error == "ticket_closed":
        raise HTTPException(
            status_code=400,
            detail="Cannot delete comments on a closed ticket"
        )

    return None

# GET my comment
@my_comments_router.get(
    "/me",
    response_model=list[CommentResponse]
)
def get_my_comments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return comment_service.get_my_comments(
        db=db,
        current_user=current_user
    )
