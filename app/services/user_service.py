from sqlalchemy.orm import Session

from app.models.models import User
from app.schemas.user import UserCreate
from app.core.security import hash_password

# POST USER
def create_user(db: Session, user_data: UserCreate):
    hashed_password = hash_password(user_data.password)

    user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=hashed_password,
        role=user_data.role
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user
  
# GET all users
def get_users(db: Session):
    return db.query(User).all()


# GET user by ID
def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(
        User.id == user_id
    ).first()


# DELETE user
def delete_user(db: Session, user: User):
    db.delete(user)
    db.commit()