from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models.models import (
    Comment,
    CommentReaction,
    ReactionType,
    Ticket,
    TicketStatus,
    User
)

from app.schemas.comment_reaction import CommentReactionCreate
from app.services.comment_service import can_access_ticket


def create_or_update_reaction(
    db: Session,
    comment_id: int,
    reaction_data: CommentReactionCreate,
    current_user: User
):
    try:
        comment = db.query(Comment).filter(
            Comment.id == comment_id
        ).first()

        if comment is None:
            return None, "comment_not_found"

        ticket = db.query(Ticket).filter(
            Ticket.id == comment.ticket_id,
            Ticket.is_deleted.is_(False)
        ).with_for_update().first()

        if ticket is None:
            db.rollback()
            return None, "comment_not_found"

        if not can_access_ticket(ticket, current_user):
            db.rollback()
            return None, "permission_denied"

        if ticket.status == TicketStatus.CLOSED:
            db.rollback()
            return None, "ticket_closed"

        reaction = db.query(CommentReaction).filter(
            CommentReaction.comment_id == comment_id,
            CommentReaction.user_id == current_user.id
        ).first()

        if reaction is None:
            reaction = CommentReaction(
                comment_id=comment_id,
                user_id=current_user.id,
                reaction_type=reaction_data.reaction_type
            )

            db.add(reaction)

        else:
            reaction.reaction_type = reaction_data.reaction_type

        db.commit()
        db.refresh(reaction)

        return reaction, None

    except SQLAlchemyError:
        db.rollback()
        raise


def get_comment_reactions(
    db: Session,
    comment_id: int,
    current_user: User
):
    comment = db.query(Comment).join(
        Ticket, Comment.ticket_id == Ticket.id
    ).filter(
        Comment.id == comment_id,
        Ticket.is_deleted.is_(False)
    ).first()

    if comment is None:
        return None, "comment_not_found"

    if not can_access_ticket(comment.ticket, current_user):
        return None, "permission_denied"

    reactions = db.query(CommentReaction).filter(
        CommentReaction.comment_id == comment_id
    ).order_by(
        CommentReaction.created_at.asc(),
        CommentReaction.id.asc()
    ).all()

    thumbs_up_count = sum(
        1 for reaction in reactions
        if reaction.reaction_type == ReactionType.THUMBS_UP
    )

    thumbs_down_count = sum(
        1 for reaction in reactions
        if reaction.reaction_type == ReactionType.THUMBS_DOWN
    )

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
    try:
        comment = db.query(Comment).filter(
            Comment.id == comment_id
        ).first()

        if comment is None:
            return "comment_not_found"

        ticket = db.query(Ticket).filter(
            Ticket.id == comment.ticket_id,
            Ticket.is_deleted.is_(False)
        ).with_for_update().first()

        if ticket is None:
            db.rollback()
            return "comment_not_found"

        if not can_access_ticket(ticket, current_user):
            db.rollback()
            return "permission_denied"

        if ticket.status == TicketStatus.CLOSED:
            db.rollback()
            return "ticket_closed"

        reaction = db.query(CommentReaction).filter(
            CommentReaction.comment_id == comment_id,
            CommentReaction.user_id == current_user.id
        ).first()

        if reaction is None:
            db.rollback()
            return "reaction_not_found"

        db.delete(reaction)
        db.commit()

        return None

    except SQLAlchemyError:
        db.rollback()
        raise
