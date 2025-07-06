from pydantic import BaseModel


# Request model for login
class LoginRequest(BaseModel):
    username: str
    password: str


# Response model for login
class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    username: str
