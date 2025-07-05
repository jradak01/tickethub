import pytest
from unittest.mock import AsyncMock, patch
from fastapi import HTTPException
from src.services.auth_service import authenticate_user
from src.models.auth_model import LoginRequest
import httpx


# Test case for successful user authentication
@pytest.mark.asyncio
async def test_authenticate_user_success():
    # Create a mock HTTP response simulating a successful login
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json = lambda: {
        "accessToken": "valid_access_token",
        "refreshToken": "valid_refresh_token",
        "username": "valid_user"
    }

    # Prepare login request data
    login_data = LoginRequest(username="valid_user", password="valid_password")

    # Patch the HTTP POST request to the auth service to return the mock response
    with patch("src.services.auth_service.httpx.AsyncClient.post", return_value=mock_response):
        # Call the function under test
        result = await authenticate_user(login_data)

        # Verify that the result matches expected values from the mock response
        assert result["access_token"] == "valid_access_token"
        assert result["refresh_token"] == "valid_refresh_token"
        assert result["username"] == "valid_user"