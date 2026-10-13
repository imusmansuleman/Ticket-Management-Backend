from pwdlib import PasswordHash
from datetime import datetime, timedelta, timezone
import jwt
from app.core.config import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)

#This line creates our password-hashing object
password_hash = PasswordHash.recommended()
#an object that has been customized and loaded with specific settings so it knows exactly how to do its job.

def hash_password(password: str) -> str:
    return password_hash.hash(password)
  
# Password
def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    return password_hash.verify(
        plain_password,
        hashed_password
    )
    
    
  #create_access_token({"sub": "1"})


def create_access_token(data: dict) -> str:
    to_encode = data.copy() # why copy, what happens if we use data directly

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return encoded_jwt