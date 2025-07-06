from fastapi import FastAPI, Request
from src.routers import (
    ticket_router as tickets,
    stats_router as stats,
    auth_router as auth,
)

from src.utils.middleware import RequestInfoMiddleware
from src.utils.error_handlers import (
    http_exception_handler,
    validation_exception_handler,
    global_exception_handler,
)
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from slowapi import Limiter
from slowapi.util import get_remote_address


app = FastAPI()

limiter = Limiter(key_func=get_remote_address)


# Add middleware to log request information
app.add_middleware(RequestInfoMiddleware)
# Custom exception handlers
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)


# Root endpoint to check if the API is running
@app.get("/")
@limiter.limit("50/minute")
def root(request: Request):
    return {"message": "Hello TicketHub!"}


@app.get("/health/")
def liveness_check():
    return {"status": "ok"}


# Include the tickets router
app.include_router(tickets.router)
# Include the stats router
app.include_router(stats.router)
# Include the auth router
app.include_router(auth.router)
