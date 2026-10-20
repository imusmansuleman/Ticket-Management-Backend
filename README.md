# Ticket Management System — Backend

A RESTful API built with FastAPI for managing support tickets, user assignments, comments, and ticket activity history.

## Tech Stack

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy ORM
- Alembic
- Pydantic
- JWT Authentication

## Features

### Authentication and Authorization
- User registration and login
- JWT-based authentication
- Role-based access control (Admin, Employee, Engineer)

### Ticket Management
- Employees can create tickets
- Admins can assign tickets to engineers
- Engineers can view assigned tickets
- Ticket status management
- Ticket history tracking

### Comments
- Add comments to tickets
- View ticket comments
- Update and delete your own comments

### Comment Reactions
- Add thumbs-up or thumbs-down reactions
- Update existing reactions
- Remove your own reactions
- View reaction counts for each comment

## Project Structure

    Ticket-Management-Backend/
    ├── app/
    │   ├── core/
    │   ├── db/
    │   ├── dependencies/
    │   ├── models/
    │   ├── routers/
    │   ├── schemas/
    │   └── services/
    ├── alembic/
    ├── main.py
    ├── alembic.ini
    ├── requirements.txt
    └── README.md

## Local Setup

### 1. Clone the Repository

    git clone https://github.com/imusmansuleman/Ticket-Management-Backend.git
    cd Ticket-Management-Backend

### 2. Create a Virtual Environment

    python3 -m venv .venv
    source .venv/bin/activate

### 3. Install Dependencies

    pip install -r requirements.txt

### 4. Configure Environment Variables

Create a `.env` file in the project root and add:

```env
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

DB_USERNAME=postgres
DB_PASSWORD=your_password_here
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_database_name



### 5. Run Database Migrations

    alembic upgrade head

### 6. Start the FastAPI Server

    uvicorn main:app --reload

## API Documentation

Once the application is running, open:

http://127.0.0.1:8000/docs

Swagger UI provides interactive documentation for
testing the available endpoints.
