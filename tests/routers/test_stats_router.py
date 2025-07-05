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
    mocker.patch('src.routers.auths.authenticate_user', mock)

    # Return the mock object so it can be used in test cases
    return mock