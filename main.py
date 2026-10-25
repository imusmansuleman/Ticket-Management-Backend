from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import users, tickets, auth
from app.routers import comments, comment_reactions, ticket_history

app = FastAPI()

# Allow requests from our React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(users.router)
app.include_router(ticket_history.router)
app.include_router(tickets.router)
app.include_router(auth.router)
app.include_router(comments.router)
app.include_router(comments.my_comments_router)
app.include_router(comment_reactions.router)


@app.get("/")
def root():
    return {
        "message": "Ticket System API is working"
    }
