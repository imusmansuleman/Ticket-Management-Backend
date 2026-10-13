from fastapi import APIRouter, Depends, HTTPException, status
#Depends is FastAPI’s dependency injection mechanism. In simple terms, it tells FastAPI:
#Before running this endpoint, run some other function and use its result here.
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.models import User
from app.schemas.user import UserLogin
from app.core.security import create_access_token
from app.services import auth_service

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/login")
def login(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    user = auth_service.authenticate_user(
        db=db,
        email=login_data.email,
        password=login_data.password
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    access_token = create_access_token(
        {"sub": str(user.id)}
    )

    return {
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "role": user.role
    }