from sqlalchemy.orm import Session

from app.models.models import TicketHistory, Ticket

#defines a reusable Python function.
def create_history(
    db: Session,
    ticket_id: int,
    changed_by_id: int,
    action: str,
    field_name: str | None = None,
    old_value: str | None = None,
    new_value: str | None = None
):
  #At this point, the object exists in Python memory, but it hasn't been inserted into PostgreSQL.
  #history is a variable holding that newly created object.
    history = TicketHistory(
        ticket_id=ticket_id,
        changed_by_id=changed_by_id,
        action=action,
        field_name=field_name,
        old_value=old_value,
        new_value=new_value
    )

    db.add(history)

    return history
  
# 1. Get history of a specific ticket
def get_ticket_history(
    db: Session,
    ticket_id: int
):
    ticket = db.query(Ticket).filter(
        Ticket.id == ticket_id
    ).first()

    if ticket is None:
        return None

    return db.query(TicketHistory).filter(
        TicketHistory.ticket_id == ticket_id
    ).order_by(
        TicketHistory.created_at.asc(),
        TicketHistory.id.asc()
    ).all()

# 2. Get history of all tickets
def get_all_ticket_history(db: Session):
    return db.query(TicketHistory).order_by(
        TicketHistory.created_at.desc(),
        TicketHistory.id.desc()
    ).all()