from sqlalchemy.orm import Session

from app.models.models import User
from app.core.security import verify_password


def authenticate_user(
    db: Session,
    email: str,
    password: str
):
    user = db.query(User).filter(
        User.email == email
    ).first()

    if user is None:
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user