import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock
from src.main import app
from src.models.auth_model import LoginResponse

# Create a TestClient instance for interacting with the FastAPI app
client = TestClient(app)


# Fixture to mock the 'authenticate_user' function
@pytest.fixture
def mock_authenticate_user(mocker):
    # Create an AsyncMock object to mock the asynchronous behavior of 'authenticate_user'
    mock = AsyncMock()

    # Patch the 'authenticate_user' function in the 'src.routers.auths' module with the mock object
    mocker.patch("src.routers.auth_router.authenticate_user", mock)

    # Return the mock object so it can be used in test cases
    return mock


# Test case for the login endpoint, using the mock_authenticate_user fixture
@pytest.mark.asyncio
async def test_login(mock_authenticate_user):
    # Mock the return value of the 'authenticate_user' function
    mock_authenticate_user.return_value = LoginResponse(
        access_token="mocked_access_token",  # Mocked access token
        token_type="bearer",  # Token type
        refresh_token="mocked_refresh_token",  # Mocked refresh token
        username="test_user",  # Mocked username
    )

    # Mock login request data
    login_data = {
        "username": "testuser",  # Mocked username
        "password": "testpassword",  # Mocked password
    }

    # Make a POST request to the '/auth/login' endpoint with the login data
    response = client.post("/auth/login", json=login_data)

    # Check that the response status code is 200 (success)
    assert response.status_code == 200

    # Parse the response JSON data
    data = response.json()

    # Check if the response contains the expected tokens and username
    assert "access_token" in data  # Ensure 'access_token' is present in the response
    assert (
        data["access_token"] == "mocked_access_token"
    )  # Check if the access token matches the mock value

    assert "refresh_token" in data  # Ensure 'refresh_token' is present in the response
    assert (
        data["refresh_token"] == "mocked_refresh_token"
    )  # Check if the refresh token matches the mock value

    assert "username" in data  # Ensure 'username' is present in the response
    assert (
        data["username"] == "test_user"
    )  # Check if the username matches the mock value


# Test case for a successful login scenario
@pytest.mark.asyncio
async def test_login_success():

    # Mock login data for a valid user
    login_data = {
        "username": "emilys",  # Valid username
        "password": "emilyspass",  # Correct password
    }

    # Make a POST request to the '/auth/login' endpoint with the login data
    response = client.post("/auth/login", json=login_data)

    # Assert that the response status code is 200 (success)
    assert response.status_code == 200

    # Parse the response JSON data
    data = response.json()

    # Assert that the response contains the expected tokens and username
    assert "access_token" in data  # Ensure 'access_token' is present in the response
    assert "refresh_token" in data  # Ensure 'refresh_token' is present in the response
    assert "username" in data  # Ensure 'username' is present in the response
    assert data["username"] == "emilys"  # Ensure the username matches the mock value


# Test case for an invalid login scenario (incorrect username/password)
@pytest.mark.asyncio
async def test_login_invalid_crendentials():

    # Mock login data for an invalid user
    login_data = {
        "username": "emilys1",  # Invalid username
        "password": "emilyspass1",  # Incorrect password
    }

    # Make a POST request to the '/auth/login' endpoint with the login data
    response = client.post("/auth/login", json=login_data)

    # Assert that the response status code is 400 (bad request) for invalid credentials
    assert response.status_code == 400


# Test case for login with incomplete data: missing password
@pytest.mark.asyncio
async def test_login_with_incomplete_data_password(mock_authenticate_user):
    # Send incomplete login data (e.g., missing password)
    login_data = {
        "username": "testuser",  # 'password' is missing
    }

    # Simulate a POST request to the /auth/login endpoint with the incomplete data
    response = client.post("/auth/login", json=login_data)

    # Test will fail as 'token_type' is expected in the response, but it's missing due to incomplete data
    assert (
        response.status_code == 422
    )  # Expected error due to invalid request (422 Unprocessable Entity)

    # Check the response content, it should be an error response due to missing data
    data = response.json()

    # Assert that the error is contained within the 'detail' field
    assert "detail" in data

    # Check that the 'password' is marked as missing in the 'loc' field
    assert ["body", "password"] == data["detail"][0]["loc"]


# Test case for login with incomplete data: missing username
@pytest.mark.asyncio
async def test_login_with_incomplete_data_username(mock_authenticate_user):
    # Send incomplete login data (e.g., missing username)
    login_data = {
        "password": "testpassword",  # 'username' is missing
    }

    # Simulate a POST request to the /auth/login endpoint with the incomplete data
    response = client.post("/auth/login", json=login_data)

    # Test will fail as 'token_type' is expected in the response, but it's missing due to incomplete data
    assert (
        response.status_code == 422
    )  # Expected error due to invalid request (422 Unprocessable Entity)

    # Check the response content, it should be an error response due to missing data
    data = response.json()

    # Assert that the error is contained within the 'detail' field
    assert "detail" in data

    # Check that the 'username' is marked as missing in the 'loc' field
    assert ["body", "username"] == data["detail"][0]["loc"]


# Test case for login with completely missing data
@pytest.mark.asyncio
async def test_login_with_incomplete_data(mock_authenticate_user):
    # Send incomplete login data (e.g., no username or password)
    login_data = {
        # Both 'username' and 'password' are missing
    }

    # Simulate a POST request to the /auth/login endpoint with the incomplete data
    response = client.post("/auth/login", json=login_data)

    # Test will fail because 'token_type' is expected in the response, but it's missing due to the incomplete data
    assert (
        response.status_code == 422
    )  # Expected error due to invalid request (422 Unprocessable Entity)

    # Check the response content, it should be an error response due to missing data
    data = response.json()

    # Assert that the error is contained within the 'detail' field
    assert "detail" in data

    # Check that both 'username' and 'password' are marked as missing in the 'loc' field
    assert ["body", "username"] == data["detail"][0]["loc"]  # 'username' is missing
    assert ["body", "password"] == data["detail"][1]["loc"]  # 'password' is missing
