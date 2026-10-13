from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.models import User, Ticket, TicketHistory, UserRole
from app.dependencies.auth import get_current_user
from app.schemas.ticket_history import TicketHistoryResponse


router = APIRouter(
    prefix="/tickets",
    tags=["Ticket History"]
)


@router.get(
    "/{ticket_id}/history",
    response_model=list[TicketHistoryResponse]
)
def get_ticket_history(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ticket = db.query(Ticket).filter(
        Ticket.id == ticket_id
    ).first()

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    allowed = (
        current_user.role == UserRole.ADMIN
        or ticket.created_by_id == current_user.id
        or ticket.assignee_id == current_user.id
    )

    if not allowed:
        raise HTTPException(
            status_code=403,
            detail="You cannot view this ticket's history"
        )

    history = db.query(TicketHistory).filter(
        TicketHistory.ticket_id == ticket_id
    ).order_by(
        TicketHistory.created_at.asc(),
        TicketHistory.id.asc()
    ).all()

    return history
