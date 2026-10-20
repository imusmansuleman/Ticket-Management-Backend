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

from datetime import datetime
from pydantic import BaseModel, ConfigDict


class TicketResponse(BaseModel):
    id: int
    title: str
    status: str
    is_deleted: bool
    deleted_at: datetime | None = None
    deleted_by_id: int | None = None

    model_config = ConfigDict(from_attributes=True)
