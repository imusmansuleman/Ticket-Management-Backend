
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.models import ReactionType

from app.models.models import (
    Comment,
    CommentReaction,
    TicketStatus,
    User,
    UserRole
)

from app.schemas.comment_reaction import CommentReactionCreate


def create_or_update_reaction(
    db: Session,
    comment_id: int,
    reaction_data: CommentReactionCreate,
    current_user: User
):
    # Step 1: Find the comment
    comment = db.query(Comment).filter(
        Comment.id == comment_id
    ).first()

    if comment is None:
        return None, "comment_not_found"

    # Step 2: Get the associated ticket
    ticket = comment.ticket

    # Step 3: Check ticket permissions
    allowed = (
        current_user.role == UserRole.ADMIN
        or (
            current_user.role == UserRole.EMPLOYEE
            and ticket.created_by_id == current_user.id
        )
        or (
            current_user.role == UserRole.ENGINEER
            and ticket.assignee_id == current_user.id
        )
    )

    if not allowed:
        return None, "permission_denied"

    # Step 4: Check ticket status
    if ticket.status == TicketStatus.CLOSED:
        return None, "ticket_closed"

    # Step 5: Check for an existing reaction
    reaction = db.query(CommentReaction).filter(
        CommentReaction.comment_id == comment_id,
        CommentReaction.user_id == current_user.id
    ).first()

    try:
        if reaction is None:
            # Create a new reaction
            reaction = CommentReaction(
                comment_id=comment_id,
                user_id=current_user.id,
                reaction_type=reaction_data.reaction_type
            )

            db.add(reaction)

        else:
            # Update the existing reaction
            reaction.reaction_type = reaction_data.reaction_type

        db.commit()

    except SQLAlchemyError:
        db.rollback()
        raise

    db.refresh(reaction)

    return reaction, None



def get_comment_reactions(
    db: Session,
    comment_id: int,
    current_user: User
):
    # Step 1: Find the comment
    comment = db.query(Comment).filter(
        Comment.id == comment_id
    ).first()

    if comment is None:
        return None, "comment_not_found"

    # Step 2: Get the associated ticket
    ticket = comment.ticket

    # Step 3: Check permissions
    allowed = (
        current_user.role == UserRole.ADMIN
        or (
            current_user.role == UserRole.EMPLOYEE
            and ticket.created_by_id == current_user.id
        )
        or (
            current_user.role == UserRole.ENGINEER
            and ticket.assignee_id == current_user.id
        )
    )

    if not allowed:
        return None, "permission_denied"
      
      

    # Step 4: Retrieve all reactions
    reactions = db.query(CommentReaction).filter(
        CommentReaction.comment_id == comment_id
    ).order_by(
        CommentReaction.created_at.asc(),
        CommentReaction.id.asc()
    ).all()

    # Step 5: Count reactions
    thumbs_up_count = sum(
        1 for reaction in reactions
        if reaction.reaction_type == ReactionType.THUMBS_UP
    )

    thumbs_down_count = sum(
        1 for reaction in reactions
        if reaction.reaction_type == ReactionType.THUMBS_DOWN
    )

    # Step 6: Build response
    result = {
        "comment_id": comment_id,
        "total_reactions": len(reactions),
        "thumbs_up_count": thumbs_up_count,
        "thumbs_down_count": thumbs_down_count,
        "reactions": reactions
    }

    return result, None
  
  

def delete_reaction(
    db: Session,
    comment_id: int,
    current_user: User
):
    # Step 1: Check whether the comment exists
    comment = db.query(Comment).filter(
        Comment.id == comment_id
    ).first()

    if comment is None:
        return "comment_not_found"

    # Step 2: Get the associated ticket
    ticket = comment.ticket

    # Step 3: Check ticket permissions
    allowed = (
        current_user.role == UserRole.ADMIN
        or (
            current_user.role == UserRole.EMPLOYEE
            and ticket.created_by_id == current_user.id
        )
        or (
            current_user.role == UserRole.ENGINEER
            and ticket.assignee_id == current_user.id
        )
    )

    if not allowed:
        return "permission_denied"

    # Step 4: Check ticket status
    if ticket.status == TicketStatus.CLOSED:
        return "ticket_closed"

    # Step 5: Find the user's reaction
    reaction = db.query(CommentReaction).filter(
        CommentReaction.comment_id == comment_id,
        CommentReaction.user_id == current_user.id
    ).first()

    if reaction is None:
        return "reaction_not_found"

    # Step 6: Delete the reaction
    try:
        db.delete(reaction)
        db.commit()

    except SQLAlchemyError:
        db.rollback()
        raise

    return None

