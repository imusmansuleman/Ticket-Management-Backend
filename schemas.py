from datetime import datetime

from pydantic import BaseModel, EmailStr

from app.models.models import (
    UserRole,
    TicketCategory,
    TicketStatus,
    TicketPriority,
)

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: UserRole


class TicketCreate(BaseModel):
    category: TicketCategory
    status: TicketStatus
    priority: TicketPriority
    created_by_id: int
    assignee_id: int | None = None
    title: str
    description: str
    due_date: datetime | None = None
    
class UserLogin(BaseModel):
    email: EmailStr
    password: str