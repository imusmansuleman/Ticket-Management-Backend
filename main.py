from fastapi import FastAPI
from app.routers import users, tickets, auth
from app.routers import comments, comment_reactions


# Base.metadata.create_all(bind=engine)

print("Tables created successfully")


app = FastAPI()

app.include_router(users.router)
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
