import pytest
from unittest.mock import AsyncMock, patch
from src.services.user_service import get_users_count
from fastapi import HTTPException
from httpx import HTTPStatusError, Response, Request

# Test cases for get_users_count function in user_service
@pytest.mark.asyncio
async def test_get_users_count_success():
    with patch("src.services.user_service.get_cache", return_value=None), patch("src.services.user_service.set_cache"):
        # Mocking the response from the HTTP request
        mock_response = AsyncMock()
        # Simulating a successful response with a total of 20 users
        mock_response.json = lambda: {"total": 20}

        # Patching the httpx.AsyncClient.get method to return the mock response
        with patch("src.services.user_service.httpx.AsyncClient.get", return_value=mock_response):
            # Calling the get_users_count function and checking the result
            result = await get_users_count()
            # Asserting that the result is as expected
            assert result == 20

# Test cases for get_users_count function to ensure it is called with correct parameters
@pytest.mark.asyncio
async def test_get_users_count_called_with_correct_params():
    with patch("src.services.user_service.get_cache", return_value=None), patch("src.services.user_service.set_cache"):
        # Mocking the response from the HTTP request
        mock_response = AsyncMock()
        # Simulating a successful response with a total of 50 users
        mock_response.json = lambda: {"total": 50}

        # Patching the httpx.AsyncClient.get method to return the mock response
        with patch("src.services.user_service.httpx.AsyncClient.get", return_value=mock_response) as mock_get:
            # Calling the get_users_count function
            result = await get_users_count()
            # Asserting that the get method was called with the correct URL and parameters
            mock_get.assert_called_once_with("https://dummyjson.com/users", params={"limit": 1})
            assert result == 50

# Test cases for get_users_count function when the response does not contain the "total" key
@pytest.mark.asyncio
async def test_get_users_count_no_total_key():
    with patch("src.services.user_service.get_cache", return_value=None), patch("src.services.user_service.set_cache"):
        # Mocking the response from the HTTP request
        mock_response = AsyncMock()
        # Simulating a response that does not contain the "total" key
        mock_response.json = lambda: {}

        # Patching the httpx.AsyncClient.get method to return the mock response
        with patch("src.services.user_service.httpx.AsyncClient.get", return_value=mock_response):
            # Calling the get_users_count function and checking the result
            result = await get_users_count()
            # Asserting that the result is 0 when "total" key is not present
            assert result == 0  # returns 0 if "total" key is missing

# Test cases for get_users_count function when the response is not a dictionary
@pytest.mark.asyncio
async def test_get_users_count_invalid_json_format():
    with patch("src.services.user_service.get_cache", return_value=None), patch("src.services.user_service.set_cache"):
        # Mocking the response from the HTTP request
        mock_response = AsyncMock()
        # Simulating a response that is not a dictionary (e.g., a list)
        mock_response.json = lambda: ["not", "a", "dict"]

        # Patching the httpx.AsyncClient.get method to return the mock response
        with patch("src.services.user_service.httpx.AsyncClient.get", return_value=mock_response):
            # Calling the get_users_count function and checking the result
            with pytest.raises(HTTPException) as e:
                await get_users_count()
            # Asserting that an HTTPException is raised with the expected message
            assert "Unexpected error" in e.value.detail

# Test cases for get_users_count function when the JSON parsing raises an exception
@pytest.mark.asyncio
async def test_get_users_count_json_raises_exception():
    with patch("src.services.user_service.get_cache", return_value=None), patch("src.services.user_service.set_cache"):
        # Mocking the response from the HTTP request
        mock_response = AsyncMock()
        # Simulating a scenario where JSON parsing raises an exception
        async def raise_json_error():
            raise ValueError("Invalid JSON")
        # Setting the mock response's json method to raise an exception
        mock_response.json = raise_json_error

        # Patching the httpx.AsyncClient.get method to return the mock response
        with patch("src.services.user_service.httpx.AsyncClient.get", return_value=mock_response):
            # Calling the get_users_count function and checking the result
            with pytest.raises(HTTPException) as e:
                await get_users_count()
            # Asserting that an HTTPException is raised with the expected message
            assert "Unexpected error" in e.value.detail 

# Test cases for get_users_count function when HTTPStatusError is raised
@pytest.mark.asyncio
async def test_get_users_count_http_status_error():
    with patch("src.services.user_service.get_cache", return_value=None), patch("src.services.user_service.set_cache"):
        # Mocking the response from the HTTP request
        mock_response = AsyncMock()
        # Simulating an HTTPStatusError with a 500 status code
        exc = HTTPStatusError("Error", request=Request("GET", "url"), response=Response(500))

        # Defining a function to raise the HTTPStatusError
        async def raise_error(*args, **kwargs):
            raise exc
    
        # Patching the httpx.AsyncClient.get method to raise the HTTPStatusError
        with patch("src.services.user_service.httpx.AsyncClient.get", side_effect=raise_error):
            # Calling the get_users_count function and checking the result
            with pytest.raises(HTTPException) as e:
                await get_users_count()
            # Asserting that an HTTPException is raised with the expected status code and message
            assert e.value.status_code == 500
            assert "HTTP error" in e.value.detail