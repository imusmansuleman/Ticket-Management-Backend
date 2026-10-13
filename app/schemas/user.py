from pydantic import BaseModel, ConfigDict
from datetime import datetime

from pydantic import BaseModel, EmailStr
from app.models.models import (
    UserRole,
)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: UserRole

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str

    model_config = ConfigDict(from_attributes=True)