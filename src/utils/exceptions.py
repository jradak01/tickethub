from fastapi import HTTPException
from src.utils.logger import error

def log_and_raise(msg: str, status_code: int = 500) -> None:
    # Log the error message using the custom logger
    error(msg)
    # Raise an HTTPException with the given status code and message
    raise HTTPException(status_code=status_code, detail=msg)
