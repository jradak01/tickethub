import pytest
from unittest.mock import AsyncMock
from fastapi.testclient import TestClient
from src.main import app 
from src.models.ticket_model import (TicketStatus, TicketPriority, 
                                     Ticket, TicketSummary, 
                                     TicketListResponse, TicketWithRawResponse)

# Fixture to mock the 'get_ticket_by_id' function in the ticket_router
@pytest.fixture
def mock_get_ticket_by_id(mocker):
    # Create an AsyncMock to simulate the behavior of 'get_ticket_by_id'
    mock = AsyncMock()

    # Patch the 'get_ticket_by_id' function in 'src.routers.ticket_router' with the mock
    mocker.patch('src.routers.ticket_router.get_ticket_by_id', mock)

    # Return the mock to be used in test cases
    return mock

# Fixture to mock the get_tickets function in the src.routers.tickets module
@pytest.fixture
def mock_get_tickets(mocker):
    # Create a mock object for the get_tickets function
    mock = AsyncMock()
    
    # Use patching to replace the original get_tickets function with the mock
    mocker.patch('src.routers.ticket_router.get_tickets', mock)
    
    # Return the mocked object so it can be used in tests
    return mock


# Test case for the /tickets/{id} route (valid ticket retrieval)
@pytest.mark.asyncio
async def test_get_ticket_valid(mock_get_ticket_by_id):
    # Mock the response for 'get_ticket_by_id' function
    mock_get_ticket_by_id.return_value = {
        "ticket": {
            "id": 1,
            "title": "Do something nice for someone you care about",
            "status": "open",
            "priority": "medium",
            "assignee": "paisleyf"
        },
        "raw": {
            "id": 1,
            "todo": "Do something nice for someone you care about",
            "completed": False,
            "userId": 152
        }
    }

    # Create TestClient instance (used for testing FastAPI routes)
    client = TestClient(app)
    
    # Send GET request to /tickets/1 route
    response = client.get("/tickets/1")

    # Check if the status code of the response is 200 (successful)
    assert response.status_code == 200

    # Validate the response JSON to ensure it matches the mock data
    assert response.json() == {
        "ticket": {
            "id": 1,
            "title": "Do something nice for someone you care about",
            "status": "open",
            "priority": "medium",
            "assignee": "paisleyf"
        },
        "raw": {
            "id": 1,
            "todo": "Do something nice for someone you care about",
            "completed": False,
            "userId": 152
        }
    }

# Test case for the /tickets/{id} route (ticket not found scenario)
@pytest.mark.asyncio
async def test_get_ticket_not_found(mock_get_ticket_by_id):
    # Mock the case where get_ticket_by_id raises an exception (ticket not found)
    mock_get_ticket_by_id.side_effect = Exception("Ticket not found")

    # Create TestClient instance (used for testing FastAPI routes)
    client = TestClient(app)
    
    # Send GET request to /tickets/9999 route (a non-existent ticket)
    response = client.get("/tickets/9999")

    # Check if the status code of the response is 500 (internal server error)
    assert response.status_code == 500

