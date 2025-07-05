from fastapi import FastAPI
from src.routers import (ticket_router as tickets, 
                         stats_router as stats,
                         auth_router as auth)

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello TicketHub!"}

# Include the tickets router
app.include_router(tickets.router)
# Include the stats router
app.include_router(stats.router)
# Include the auth router
app.include_router(auth.router)