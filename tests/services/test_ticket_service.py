import pytest
from unittest.mock import AsyncMock, Mock, patch
from src.services.ticket_service import get_tickets, get_ticket_by_id
from fastapi import HTTPException
from src.models.ticket_model import Ticket, TicketStatus, TicketPriority, TicketWithRawResponse
import httpx

# Test case for get_tickets function with successful response
@pytest.mark.asyncio
async def test_get_tickets_success():
# Patch cache functions to avoid real Redis calls during the test
    with patch("src.services.ticket_service.get_cache", return_value=None), \
         patch("src.services.ticket_service.set_cache"):
        
        # Mock response from the /todos endpoint
        mock_todos_response = AsyncMock()
        mock_todos_response.json = lambda: {
            "total": 10,
            "todos": [
                {
                    "id": 1,
                    "todo": "Some Todo",
                    "completed": False,
                    "userId": 1
                }
            ]
        }

        # Mock response from the /users endpoint
        mock_users_response = AsyncMock()
        mock_users_response.json = lambda: {
            "total": 1,
            "users": [
                {
                    "id": 1,
                    "username": "test_user"
                }
            ]
        }

        # Patch the AsyncClient.get method to return mock responses in order
        # The function likely calls /todos and /users twice (maybe for caching or internal logic)
        with patch("src.services.ticket_service.httpx.AsyncClient.get", 
                   side_effect=[mock_todos_response, mock_users_response, 
                                mock_todos_response, mock_users_response]):
            # Call the function under test
            tickets = await get_tickets()

        # Assert that one ticket was returned
        assert len(tickets["tickets"]) == 1
        # Assert ticket data matches expected values
        assert tickets["tickets"][0].id == 1
        assert tickets["tickets"][0].title == "Some Todo"
        assert tickets["tickets"][0].status == TicketStatus.open


# Test case for get_tickets function with no tickets found
@pytest.mark.asyncio
async def test_get_tickets_unexpected_error():
    # Patch cache functions to bypass actual Redis interaction
    with patch("src.services.ticket_service.get_cache", return_value=None), \
         patch("src.services.ticket_service.set_cache"):
        
        # Create a mock response that raises an HTTPStatusError when raise_for_status is called
        mock_todos_response = AsyncMock()
        mock_todos_response.raise_for_status = AsyncMock(
            side_effect=httpx.HTTPStatusError("500 Internal Server Error", request=None, response=None)
        )
        mock_todos_response.json = AsyncMock(return_value={"total": 10})  # This won't be used due to the error

        # Patch the HTTP GET request to return the faulty mock response
        with patch("src.services.ticket_service.httpx.AsyncClient.get", return_value=mock_todos_response):
            # Expect the get_tickets function to raise an HTTPException due to the internal error
            with pytest.raises(HTTPException) as e:
                await get_tickets()

            # Assert that the raised exception has the correct status code and error message
            assert e.value.status_code == 500
            assert "Unexpected error in get_tickets" in e.value.detail