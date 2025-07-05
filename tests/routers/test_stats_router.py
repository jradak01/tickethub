import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
from src.main import app
from src.models.auth_model import LoginRequest, LoginResponse
from src.services.auth_service import authenticate_user

# Create a TestClient instance for interacting with the FastAPI app
client = TestClient(app)

# Fixture to mock the 'authenticate_user' function
@pytest.fixture
def mock_authenticate_user(mocker):
    # Create an AsyncMock object to mock the asynchronous behavior of 'authenticate_user'
    mock = AsyncMock()

    # Patch the 'authenticate_user' function in the 'src.routers.auths' module with the mock object
    mocker.patch('src.routers.auth_router.authenticate_user', mock)

    # Return the mock object so it can be used in test cases
    return mock

# Test case for the login endpoint, using the mock_authenticate_user fixture
@pytest.mark.asyncio
async def test_login(mock_authenticate_user):
    # Mock the return value of the 'authenticate_user' function
    mock_authenticate_user.return_value = LoginResponse(
        access_token="mocked_access_token",  # Mocked access token
        token_type="bearer",                 # Token type
        refresh_token="mocked_refresh_token",  # Mocked refresh token
        username="test_user"                 # Mocked username
    )

    # Mock login request data
    login_data = {
        "username": "testuser",  # Mocked username
        "password": "testpassword"  # Mocked password
    }

    # Make a POST request to the '/auth/login' endpoint with the login data
    response = client.post("/auth/login", json=login_data)

    # Check that the response status code is 200 (success)
    assert response.status_code == 200

    # Parse the response JSON data
    data = response.json()

    # Check if the response contains the expected tokens and username
    assert "access_token" in data  # Ensure 'access_token' is present in the response
    assert data["access_token"] == "mocked_access_token"  # Check if the access token matches the mock value

    assert "refresh_token" in data  # Ensure 'refresh_token' is present in the response
    assert data["refresh_token"] == "mocked_refresh_token"  # Check if the refresh token matches the mock value

    assert "username" in data  # Ensure 'username' is present in the response
    assert data["username"] == "test_user"  # Check if the username matches the mock value
