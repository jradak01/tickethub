from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from src.utils.logger import info


# Middleware to log request information
class RequestInfoMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Log request information
        info("Method:", request.method)
        info("Path:", str(request.url))
        try:
            # Log headers
            body = await request.body()
            info("Body:", body.decode() if body else "No body")
        except Exception:
            # If body is not available, log a warning
            info("Body: not available")
        info("---")
        response = await call_next(request)
        return response
