import pytest
from unittest.mock import AsyncMock, patch
from src.services.user_service import get_users_count
from fastapi import HTTPException

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
