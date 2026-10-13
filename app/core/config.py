import os

from dotenv import load_dotenv


load_dotenv()
#  #create_access_token({"sub": "1"})
SECRET_KEY = os.getenv("SECRET_KEY") # NAME KEY
#os.getenv() works with environment variable values as strings.
ALGORITHM = os.getenv("ALGORITHM", "HS256") # NAME ENV VARIABLE SPECIFICALLY
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")  # NAME ENV VARIABLE SPECIFICALLY
)


if not SECRET_KEY:
    raise RuntimeError(
        "SECRET_KEY environment variable is not set"
    )