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