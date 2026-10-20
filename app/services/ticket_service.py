from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timezone
from app.services.ticket_history_service import create_history
from app.models.models import Ticket, TicketStatus, User, UserRole
from app.schemas.ticket import TicketCreate

# 1. Employee creates a ticket
def create_ticket(
    db: Session,
    ticket_data: TicketCreate,
    current_user_id: int
):
    ticket = Ticket(
        category=ticket_data.category,
        status=TicketStatus.OPEN,
        priority=ticket_data.priority,
        created_by_id=current_user_id,
        assignee_id=None,
        title=ticket_data.title,
        description=ticket_data.description,
        due_date=ticket_data.due_date
    )

    try:
        db.add(ticket)
        db.flush()

        create_history(
            db=db,
            ticket_id=ticket.id,
            changed_by_id=current_user_id,
            action="created",
            field_name="status",
            old_value=None,
            new_value=TicketStatus.OPEN.value
        )

        db.commit()

    except SQLAlchemyError:
        db.rollback()
        raise

    db.refresh(ticket)
    return ticket


# def create_ticket(
#     db: Session,
#     ticket_data: TicketCreate,
#     current_user_id: int
# ):
#     ticket = Ticket(
#         category=ticket_data.category,
#         status=ticket_data.status,
#         priority=ticket_data.priority,
#         created_by_id=current_user_id,
#         assignee_id=ticket_data.assignee_id,
#         title=ticket_data.title,
#         description=ticket_data.description,
#         due_date=ticket_data.due_date
#     )

#     db.add(ticket)
#     db.commit()
#     db.refresh(ticket)

#     return ticket


# 2. Admin assigns a ticket to an engineer
def assign_ticket(
    db: Session,
    ticket_id: int,
    assignee_id: int,
    current_user_id: int
):
    try:
        ticket = db.query(Ticket).filter(
            Ticket.id == ticket_id,
            Ticket.is_deleted.is_(False)
        ).with_for_update().first()

        if ticket is None:
            db.rollback()
            return None, "ticket_not_found"

        engineer = db.query(User).filter(
            User.id == assignee_id
        ).first()

        if engineer is None:
            db.rollback()
            return None, "user_not_found"

        if engineer.role != UserRole.ENGINEER:
            db.rollback()
            return None, "not_engineer"

        if ticket.assignee_id == engineer.id:
            db.rollback()
            return None, "already_assigned"

        old_assignee_id = ticket.assignee_id

        ticket.assignee_id = engineer.id

        create_history(
            db=db,
            ticket_id=ticket.id,
            changed_by_id=current_user_id,
            action="assigned",
            field_name="assignee_id",
            old_value=(
                str(old_assignee_id)
                if old_assignee_id is not None
                else None
            ),
            new_value=str(engineer.id)
        )

        db.commit()
        db.refresh(ticket)

        return ticket, None

    except SQLAlchemyError:
        db.rollback()
        raise


# 3. get_my_created_tickets by employee
def get_my_created_tickets(
    db: Session,
    employee_id: int
):
    return db.query(Ticket).filter(
        Ticket.created_by_id == employee_id,
        Ticket.is_deleted.is_(False)
    ).all()


def get_assigned_tickets(
    db: Session,
    engineer_id: int
):
    return db.query(Ticket).filter(
        Ticket.assignee_id == engineer_id,
        Ticket.is_deleted.is_(False)
    ).all()




# 4. Engineer views their assigned tickets
def get_assigned_tickets(
    db: Session,
    engineer_id: int
):
    tickets = db.query(Ticket).filter(
        Ticket.assignee_id == engineer_id
    ).all()

    return tickets


# 5. Engineer/Admin updates ticket status
def update_ticket_status(
    db: Session,
    ticket_id: int,
    new_status: TicketStatus,
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

        if current_user.role == UserRole.ENGINEER:

            if ticket.assignee_id != current_user.id:
                db.rollback()
                return None, "not_assigned"

            valid_transition = (
                (
                    ticket.status == TicketStatus.OPEN
                    and new_status == TicketStatus.IN_PROGRESS
                )
                or
                (
                    ticket.status == TicketStatus.IN_PROGRESS
                    and new_status == TicketStatus.RESOLVED
                )
            )

            if not valid_transition:
                db.rollback()
                return None, "invalid_transition"

        elif current_user.role == UserRole.ADMIN:

            if not (
                ticket.status == TicketStatus.RESOLVED
                and new_status == TicketStatus.CLOSED
            ):
                db.rollback()
                return None, "invalid_transition"

        else:
            db.rollback()
            return None, "permission_denied"

        old_status = ticket.status
        ticket.status = new_status

        if new_status == TicketStatus.RESOLVED:
            ticket.resolved_at = datetime.now(timezone.utc)

        elif new_status == TicketStatus.CLOSED:
            ticket.closed_at = datetime.now(timezone.utc)

        create_history(
            db=db,
            ticket_id=ticket.id,
            changed_by_id=current_user.id,
            action="status_changed",
            field_name="status",
            old_value=old_status.value,
            new_value=new_status.value
        )

        db.commit()
        db.refresh(ticket)

        return ticket, None

    except SQLAlchemyError:
        db.rollback()
        raise




# 6. endpoint to retrieve all tickets
def get_all_tickets(db: Session):
    return db.query(Ticket).filter(
        Ticket.is_deleted.is_(False)
    ).order_by(Ticket.id.desc()).all()


# 7. Endpoint to retrieve a ticket by ID
def get_ticket_by_id(
    db: Session,
    ticket_id: int
):
    return db.query(Ticket).filter(
        Ticket.id == ticket_id,
        Ticket.is_deleted.is_(False)
    ).first()



# 8. soft deleting a ticket
def delete_ticket(
    db: Session,
    ticket_id: int,
    current_user: User
):
    try:
        ticket = db.query(Ticket).filter(
            Ticket.id == ticket_id
        ).with_for_update().first()

        if ticket is None:
            db.rollback()
            return None, "ticket_not_found"

        if ticket.is_deleted:
            db.rollback()
            return None, "already_deleted"

        is_admin = current_user.role == UserRole.ADMIN

        is_creator = (
            current_user.role == UserRole.EMPLOYEE
            and ticket.created_by_id == current_user.id
        )

        if not (is_admin or is_creator):
            db.rollback()
            return None, "permission_denied"

        if (
            ticket.status != TicketStatus.OPEN
            or ticket.assignee_id is not None
        ):
            db.rollback()
            return None, "deletion_not_allowed"

        ticket.is_deleted = True
        ticket.deleted_at = datetime.now(timezone.utc)
        ticket.deleted_by_id = current_user.id

        create_history(
            db=db,
            ticket_id=ticket.id,
            changed_by_id=current_user.id,
            action="deleted",
            field_name="is_deleted",
            old_value="False",
            new_value="True"
        )

        db.commit()
        db.refresh(ticket)

        return ticket, None

    except SQLAlchemyError:
        db.rollback()
        raise


# 9. Admin retrieves all soft-deleted tickets
def get_deleted_tickets(db: Session):
    return db.query(Ticket).filter(
        Ticket.is_deleted.is_(True)
    ).order_by(Ticket.deleted_at.desc()).all()

