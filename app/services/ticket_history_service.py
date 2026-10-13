from sqlalchemy.orm import Session

from app.models.models import TicketHistory

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