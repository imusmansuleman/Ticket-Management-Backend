from datetime import datetime

from pydantic import BaseModel

from app.models.models import (
    TicketStatus,
    TicketCategory,
    TicketStatus,
    TicketPriority,
)
class TicketCreate(BaseModel):
    category: TicketCategory
    priority: TicketPriority
    title: str
    description: str
    due_date: datetime | None = None
    
    
class TicketAssign(BaseModel):
    assignee_id: int
    
class TicketStatusUpdate(BaseModel):
    status: TicketStatus
  