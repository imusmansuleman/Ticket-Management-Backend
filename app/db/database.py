import os
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_URL = URL.create(
    drivername="postgresql+psycopg",
    username=os.getenv("DB_USERNAME"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT", "5432")),
    database=os.getenv("DB_NAME"),
)

engine = create_engine(DATABASE_URL)

class Base(DeclarativeBase):
    pass

#A session is the object your Python code uses to talk to the database during a unit of work.
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

#This function manages a database session for each API request:
def get_db(): #So get_db() exists mainly to manage the lifecycle of the session correctly.
    db = SessionLocal() #creates a new SQLAlchemy session.
#db is an SQLAlchemy Session object created by get_db()
    try:
        # SEARCH YIELD
        yield db #yield db hands that database session to the FastAPI endpoint that requested it.
    finally:
        db.close()
        #closes the session after the request finishes, even if something fails.