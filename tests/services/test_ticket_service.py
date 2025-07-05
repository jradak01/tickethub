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

# Test case for get_tickets function with empty response
@pytest.mark.asyncio
async def test_get_tickets_empty_response():
    # Patch cache functions to bypass Redis (simulate cache miss)
    with patch("src.services.ticket_service.get_cache", return_value=None), \
         patch("src.services.ticket_service.set_cache"):
        
        # Mock empty response for todos API
        mock_todos_response = AsyncMock()
        mock_todos_response.json = lambda: {"total": 0, "todos": []}

        # Mock empty response for users API
        mock_users_response = AsyncMock()
        mock_users_response.json = lambda: {"total": 0, "users": []}

        # Patch the HTTP GET requests to return the mocked empty responses
        with patch(
            "src.services.ticket_service.httpx.AsyncClient.get",
            side_effect=[mock_todos_response, mock_users_response, mock_todos_response, mock_users_response]
        ):
            # Call the function under test
            tickets = await get_tickets()

        # Assert that the returned tickets list is empty
        assert len(tickets["tickets"]) == 0


# Test case for get_ticket_by_id function with successful response
@pytest.mark.asyncio
async def test_get_ticket_by_id_success():
    # Patch cache-related functions to simulate a cache miss
    with patch("src.services.ticket_service.get_cache", return_value=None), \
         patch("src.services.ticket_service.set_cache"):
        
        # Mock response for the todo (ticket) API
        mock_todo_response = AsyncMock()
        mock_todo_response.json = lambda: {
            "id": 1,
            "todo": "Some Todo",
            "completed": False,
            "userId": 1
        }

        # Mock response for the user API
        mock_user_response = AsyncMock()
        mock_user_response.json = lambda: {"username": "test_user"}

        # Patch AsyncClient.get to return the mocked responses for the todo and user
        with patch(
            "src.services.ticket_service.httpx.AsyncClient.get",
            side_effect=[mock_todo_response, mock_user_response]
        ):
            # Call the function under test
            ticket_with_raw = await get_ticket_by_id(1)

        # Assertions to validate the returned ticket data
        assert ticket_with_raw.ticket.id == 1
        assert ticket_with_raw.ticket.title == "Some Todo"
        assert ticket_with_raw.ticket.status == TicketStatus.open
        assert ticket_with_raw.ticket.assignee == "test_user"
        assert ticket_with_raw.raw == mock_todo_response.json()

# Test case for get_ticket_by_id function with ticket not found
@pytest.mark.asyncio
async def test_get_ticket_by_id_not_found():
    # Patch cache-related functions to simulate a cache miss
    with patch("src.services.ticket_service.get_cache", return_value=None), \
         patch("src.services.ticket_service.set_cache"):

        # Mock response from the external API to simulate a 404 Not Found
        mock_todo_response = AsyncMock()
        mock_todo_response.status_code = 404
        mock_todo_response.json = AsyncMock(return_value={})

        # Patch AsyncClient.get to return the mocked 404 response
        with patch("src.services.ticket_service.httpx.AsyncClient.get", return_value=mock_todo_response):
            # Expect the get_ticket_by_id function to raise an HTTPException
            with pytest.raises(HTTPException) as e:
                await get_ticket_by_id(999)

            # Assertions to verify that the correct HTTPException is raised
            assert e.value.status_code == 404
            assert "Ticket with ID 999 not found" in e.value.detail

# Test case for get_ticket_by_id function with unexpected error
@pytest.mark.asyncio
async def test_get_ticket_by_id_unexpected_error():
    # Patch cache functions to simulate no cached data
    with patch("src.services.ticket_service.get_cache", return_value=None), \
         patch("src.services.ticket_service.set_cache"):

        # Create a mock response that raises an exception when .json() is called
        mock_todo_response = AsyncMock()
        mock_todo_response.json = AsyncMock(side_effect=Exception("Unexpected error"))

        # Patch the HTTP GET request to return the faulty mock response
        with patch("src.services.ticket_service.httpx.AsyncClient.get", return_value=mock_todo_response):
            # Expect get_ticket_by_id to raise an HTTPException due to the unexpected error
            with pytest.raises(HTTPException) as e:
                await get_ticket_by_id(1)

            # Verify that the raised exception has the correct status code and error message
            assert e.value.status_code == 500
            assert "Unexpected error in get_ticket_by_id" in e.value.detail