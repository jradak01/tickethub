from fastapi import APIRouter
from src.models.auth_model import LoginRequest, LoginResponse
from src.services.auth_service import authenticate_user

# Router for authentication-related endpoints
router = APIRouter(prefix="/auth", tags=["Auth"])

## try on: /docs#/ route --> { "username": "emilys", "password": "emilyspass"}
@router.post("/login", response_model=LoginResponse)
async def login(login_data: LoginRequest):
    # Authenticate user with provided login data
    token_data = await authenticate_user(login_data)

    return token_data