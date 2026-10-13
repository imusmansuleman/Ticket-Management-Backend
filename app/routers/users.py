from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.models import User
from app.dependencies.auth import require_admin
from app.schemas.user import UserCreate, UserResponse
from app.services import user_service


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)



# POST - Create user
@router.post("/", response_model=UserResponse)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    return user_service.create_user(db, user_data)
# @router.post("/")
# def create_user(
#     user_data: UserCreate,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(require_admin)
# ):
#     hashed_password = hash_password(user_data.password)

#     user = User(
#         name=user_data.name,
#         email=user_data.email,
#         password_hash=hashed_password,
#         role=user_data.role
#     )

#     db.add(user)
#     db.commit()
#     db.refresh(user)

#     return {
#         "id": user.id,
#         "full_name": user.name,
#         "email": user.email,
#         "role": user.role
#     }



# GET - All users
@router.get("/", response_model=list[UserResponse])
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    return user_service.get_users(db)
  
  
  
# GET - User by ID
@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    user = user_service.get_user_by_id(db, user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user
  
  
  
# DELETE - User
@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    user = user_service.get_user_by_id(db, user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    user_service.delete_user(db, user)

    return {
        "message": "User deleted successfully"
    }

# # DELETE
# @router.delete("/{user_id}")
# def delete_user(
#     user_id: int,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(require_admin)
# ):
#     user = db.query(User).filter(User.id == user_id).first()

#     if user is None:
#         raise HTTPException(
#             status_code=404,
#             detail="User not found"
#         )

#     db.delete(user)
#     db.commit()

#     return {
#         "message": "User deleted successfully"
#     }
