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

# Test case for authentication response missing the access token
@pytest.mark.asyncio
async def test_authenticate_user_missing_access_token():
    # Create a mock HTTP response that is missing the access token
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json = lambda: {
        "refreshToken": "valid_refresh_token",
        "username": "valid_user"
    }

    # Prepare login request data
    login_data = LoginRequest(username="valid_user", password="valid_password")

    # Patch the HTTP POST request to return the mock response
    with patch("src.services.auth_service.httpx.AsyncClient.post", return_value=mock_response):
        # Expect an HTTPException to be raised due to missing access token
        with pytest.raises(HTTPException) as e:
            await authenticate_user(login_data)

        # Verify that the correct exception is raised with appropriate status and message
        assert e.value.status_code == 500
        assert "Token not found in response" in e.value.detail

# Test case for authentication with invalid credentials
@pytest.mark.asyncio
async def test_authenticate_user_invalid_credentials():
    # Create a mock HTTP response simulating failed authentication (400 Bad Request)
    mock_response = AsyncMock()
    mock_response.status_code = 400
    mock_response.json = lambda: {}

    # Prepare login request data with invalid credentials
    login_data = LoginRequest(username="invalid_user", password="invalid_password")

    # Patch the HTTP POST request to return the mock error response
    with patch("src.services.auth_service.httpx.AsyncClient.post", return_value=mock_response):
        # Expect an HTTPException to be raised due to invalid credentials
        with pytest.raises(HTTPException) as e:
            await authenticate_user(login_data)

        # Assert that the exception has correct status code and error message
        assert e.value.status_code == 400
        assert "Invalid credentials" in e.value.detail

# Test case for authentication when the external server returns a 500 Internal Server Error
@pytest.mark.asyncio
async def test_authenticate_user_server_error():
    # Create a mock HTTP response simulating a server error (500 Internal Server Error)
    mock_response = AsyncMock()
    mock_response.status_code = 500
    mock_response.json = lambda: {}

    # Prepare login request data with valid credentials
    login_data = LoginRequest(username="valid_user", password="valid_password")

    # Patch the HTTP POST request to return the mock server error response
    with patch("src.services.auth_service.httpx.AsyncClient.post", return_value=mock_response):
        # Expect an HTTPException to be raised due to the server error
        with pytest.raises(HTTPException) as e:
            await authenticate_user(login_data)

        # Assert that the exception has correct status code and error message
        assert e.value.status_code == 500
        assert "Server error" in e.value.detail
