from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

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
    ticket = db.query(Ticket).filter(
        Ticket.id == ticket_id
    ).first()

    if ticket is None:
        return None, "ticket_not_found"

    engineer = db.query(User).filter(
        User.id == assignee_id
    ).first()

    if engineer is None:
        return None, "user_not_found"

    if engineer.role != UserRole.ENGINEER:
        return None, "not_engineer"

    if ticket.assignee_id == engineer.id:
        return None, "already_assigned"

    old_assignee_id = ticket.assignee_id

    try:
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

    except SQLAlchemyError:
        db.rollback()
        raise

    db.refresh(ticket)
    return ticket, None


# 3. get_my_created_tickets by employee
def get_my_created_tickets(
    db: Session,
    employee_id: int
):
    tickets = db.query(Ticket).filter(
        Ticket.created_by_id == employee_id
    ).all()

    return tickets



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
    current_user
):
    ticket = db.query(Ticket).filter(
        Ticket.id == ticket_id
    ).first()

    if ticket is None:
        return None, "ticket_not_found"

    # Engineer can update only their own assigned tickets
    if current_user.role == UserRole.ENGINEER:

        if ticket.assignee_id != current_user.id:
            return None, "not_assigned"

        if (
            ticket.status == TicketStatus.OPEN
            and new_status == TicketStatus.IN_PROGRESS
        ):
            pass

        elif (
            ticket.status == TicketStatus.IN_PROGRESS
            and new_status == TicketStatus.RESOLVED
        ):
            pass

        else:
            return None, "invalid_transition"

    # Admin can close resolved tickets
    elif current_user.role == UserRole.ADMIN:

        if not (
            ticket.status == TicketStatus.RESOLVED
            and new_status == TicketStatus.CLOSED
        ):
            return None, "invalid_transition"

    else:
        return None, "permission_denied"

    old_status = ticket.status

    try:
        ticket.status = new_status

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

    except SQLAlchemyError:
        db.rollback()
        raise

    db.refresh(ticket)
    return ticket, None
# 6. endpoint to retrieve all tickets
def get_all_tickets(db: Session):
    return db.query(Ticket).order_by(Ticket.id.desc()).all()
# 7. Endpoint to retrieve a ticket by ID
def get_ticket_by_id(db: Session, ticket_id: int):
    return db.query(Ticket).filter(Ticket.id == ticket_id).first()