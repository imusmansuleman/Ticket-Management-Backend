from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timezone
from app.schemas.comment import CommentUpdate
from app.models.models import Comment, Ticket, TicketStatus, User, UserRole
from app.schemas.comment import CommentCreate


def create_comment(
    db: Session,
    ticket_id: int,
    comment_data: CommentCreate,
    current_user: User
):
    ticket = db.query(Ticket).filter(
        Ticket.id == ticket_id
    ).first()

    if ticket is None:
        return None, "ticket_not_found"

    # Closed tickets cannot receive new comments
    if ticket.status == TicketStatus.CLOSED:
        return None, "ticket_closed"

    # Check whether the current user can comment
    allowed = (
        current_user.role == UserRole.ADMIN
        or ticket.created_by_id == current_user.id
        or ticket.assignee_id == current_user.id
    )

    if not allowed:
        return None, "permission_denied"

    comment = Comment(
        ticket_id=ticket.id,
        author_id=current_user.id,
        content=comment_data.content
    )

    try:
        db.add(comment)
        db.commit()

    except SQLAlchemyError:
        db.rollback()
        raise

    db.refresh(comment)

    return comment, None
  #None: Indicates there was no business-rule error.
  
  
  

def get_ticket_comments(
    db: Session,
    ticket_id: int,
    current_user: User,
    mine: bool = False
):
    ticket = db.query(Ticket).filter(
        Ticket.id == ticket_id
    ).first()

    if ticket is None:
        return None, "ticket_not_found"

    allowed = (
        current_user.role == UserRole.ADMIN
        or ticket.created_by_id == current_user.id
        or ticket.assignee_id == current_user.id
    )

    if not allowed:
        return None, "permission_denied"

    query = db.query(Comment).filter(
        Comment.ticket_id == ticket_id
    )

    if mine:
        query = query.filter(
            Comment.author_id == current_user.id
        )

    comments = query.order_by(
        Comment.created_at.asc(),
        Comment.id.asc()
    ).all()

    return comments, None

  

def update_comment(
    db: Session,
    comment_id: int,
    comment_data: CommentUpdate,
    current_user: User
):
    comment = db.query(Comment).filter(
        Comment.id == comment_id
    ).first()

    if comment is None:
        return None, "comment_not_found"

    if comment.author_id != current_user.id:
        return None, "permission_denied"

    if comment.ticket.status == TicketStatus.CLOSED:
        return None, "ticket_closed"

    comment.content = comment_data.content
    comment.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)

    try:
        db.commit()

    except SQLAlchemyError:
        db.rollback()
        raise

    db.refresh(comment)

    return comment, None
  
  
  
def delete_comment(
    db: Session,
    comment_id: int,
    current_user: User
):
    comment = db.query(Comment).filter(
        Comment.id == comment_id
    ).first()

    if comment is None:
        return "comment_not_found"

    if comment.author_id != current_user.id:
        return "permission_denied"

    if comment.ticket.status == TicketStatus.CLOSED:
        return "ticket_closed"

    try:
        db.delete(comment)
        db.commit()

    except SQLAlchemyError:
        db.rollback()
        raise

    return None
  
  
# getting all the comments of a user
def get_my_comments(
    db: Session,
    current_user: User
):
    comments = (
        db.query(Comment)
        .filter(Comment.author_id == current_user.id)
        .order_by(
            Comment.created_at.desc(),
            Comment.id.desc()
        )
        .all()
    )

    return comments

