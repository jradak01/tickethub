from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from .logger import error


# Custom exception handlers
# Handler for HTTP exceptions
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    error(f"HTTP error: {exc.detail}")
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


# Custom exception handler for request validation errors
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error("Validation error:", exc.errors())
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


# Global exception handler for unexpected errors
async def global_exception_handler(request: Request, exc: Exception):
    error("Unexpected error:", str(exc))
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
