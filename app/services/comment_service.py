from datetime import datetime, timezone
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.models import (
    Comment,
    Ticket,
    TicketStatus,
    User,
    UserRole
)
from app.schemas.comment import CommentCreate, CommentUpdate


def can_access_ticket(ticket: Ticket, current_user: User) -> bool:
    if current_user.role == UserRole.ADMIN:
        return True

    if current_user.role == UserRole.EMPLOYEE:
        return ticket.created_by_id == current_user.id

    if current_user.role == UserRole.ENGINEER:
        return ticket.assignee_id == current_user.id

    return False


def create_comment(
    db: Session,
    ticket_id: int,
    comment_data: CommentCreate,
    current_user: User
):
    try:
        ticket = db.query(Ticket).filter(
            Ticket.id == ticket_id,
            Ticket.is_deleted.is_(False)
        ).with_for_update().first()

        if ticket is None:
            db.rollback()
            return None, "ticket_not_found"

        if not can_access_ticket(ticket, current_user):
            db.rollback()
            return None, "permission_denied"

        if ticket.status == TicketStatus.CLOSED:
            db.rollback()
            return None, "ticket_closed"

        comment = Comment(
            ticket_id=ticket.id,
            author_id=current_user.id,
            content=comment_data.content
        )

        db.add(comment)
        db.commit()
        db.refresh(comment)

        return comment, None

    except SQLAlchemyError:
        db.rollback()
        raise


def get_ticket_comments(
    db: Session,
    ticket_id: int,
    current_user: User,
    mine: bool = False
):
    ticket = db.query(Ticket).filter(
        Ticket.id == ticket_id,
        Ticket.is_deleted.is_(False)
    ).first()

    if ticket is None:
        return None, "ticket_not_found"

    if not can_access_ticket(ticket, current_user):
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
    try:
        comment = db.query(Comment).filter(
            Comment.id == comment_id
        ).with_for_update().first()

        if comment is None:
            db.rollback()
            return None, "comment_not_found"

        ticket = db.query(Ticket).filter(
            Ticket.id == comment.ticket_id
        ).with_for_update().first()

        if ticket is None or ticket.is_deleted:
            db.rollback()
            return None, "comment_not_found"

        if (
            comment.author_id != current_user.id
            or not can_access_ticket(ticket, current_user)
        ):
            db.rollback()
            return None, "permission_denied"

        if ticket.status == TicketStatus.CLOSED:
            db.rollback()
            return None, "ticket_closed"

        comment.content = comment_data.content
        comment.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(comment)

        return comment, None

    except SQLAlchemyError:
        db.rollback()
        raise



def delete_comment(
    db: Session,
    comment_id: int,
    current_user: User
):
    try:
        comment = db.query(Comment).filter(
            Comment.id == comment_id
        ).with_for_update().first()

        if comment is None:
            db.rollback()
            return "comment_not_found"

        ticket = db.query(Ticket).filter(
            Ticket.id == comment.ticket_id
        ).with_for_update().first()

        if ticket is None or ticket.is_deleted:
            db.rollback()
            return "comment_not_found"

        is_admin = current_user.role == UserRole.ADMIN
        is_author = comment.author_id == current_user.id

        if not (is_admin or is_author):
            db.rollback()
            return "permission_denied"

        if not is_admin and not can_access_ticket(
            ticket, current_user
        ):
            db.rollback()
            return "permission_denied"

        if ticket.status == TicketStatus.CLOSED and not is_admin:
            db.rollback()
            return "ticket_closed"

        db.delete(comment)
        db.commit()

        return None

    except SQLAlchemyError:
        db.rollback()
        raise



def get_my_comments(
    db: Session,
    current_user: User
):
    return (
        db.query(Comment)
        .join(Ticket, Comment.ticket_id == Ticket.id)
        .filter(
            Comment.author_id == current_user.id,
            Ticket.is_deleted.is_(False)
        )
        .order_by(
            Comment.created_at.desc(),
            Comment.id.desc()
        )
        .all()
    )
