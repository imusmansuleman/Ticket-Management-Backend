from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.services import ticket_history_service
from app.db.database import get_db
from app.models.models import User, Ticket, TicketHistory, UserRole
from app.dependencies.auth import require_admin
from app.schemas.ticket_history import TicketHistoryResponse


router = APIRouter(
    prefix="/tickets",
    tags=["Ticket History"]
)


# 1. Admin gets history of all tickets
@router.get(
    "/history/all",
    response_model=list[TicketHistoryResponse]
)
def get_all_ticket_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    return ticket_history_service.get_all_ticket_history(db)



# 2. Admin gets history of a specific ticket
@router.get(
    "/{ticket_id}/history",
    response_model=list[TicketHistoryResponse]
)
def get_ticket_history(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    history = ticket_history_service.get_ticket_history(
        db=db,
        ticket_id=ticket_id
    )

    if history is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    return history

  
