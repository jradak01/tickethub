import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
from src.main import app 
from src.models.ticket_model import (TicketStatus, TicketPriority, 
                                     Ticket, TicketSummary, 
                                     TicketListResponse, TicketWithRawResponse)
from src.services.ticket_service import get_tickets
from src.services.user_service import get_users_count

# Create a TestClient instance for testing FastAPI app endpoints
client = TestClient(app)

# Fixture to mock the async function 'get_users_count' in 'src.routers.stats'
@pytest.fixture
def mock_get_users_count(mocker):
    mock = AsyncMock()  # Create an AsyncMock instance
    mocker.patch('src.routers.stats_router.get_users_count', mock)  # Patch the target function with the mock
    return mock  # Return the mock for use in tests

# Fixture to mock the async function 'get_tickets' in 'src.routers.stats'
@pytest.fixture
def mock_get_tickets(mocker):
    mock = AsyncMock()  # Create an AsyncMock instance
    mocker.patch('src.routers.stats_router.get_tickets', mock)  # Patch the target function with the mock
    return mock  # Return the mock for use in tests


# Test the /stats route
@pytest.mark.asyncio
async def test_get_stats(mock_get_tickets, mock_get_users_count):
    # Mock return values for async functions
    mock_get_users_count.return_value = 5  # Assume there are 5 users
    mock_get_tickets.return_value = {
        "tickets":[
        Ticket(id=1, title="Ticket 1", status="open", priority="low", assignee="user_1"),
        Ticket(id=2, title="Ticket 2", status="closed", priority="medium", assignee="user_1"),
        Ticket(id=3, title="Ticket 3", status="open", priority="high", assignee="user_2"),
        Ticket(id=4, title="Ticket 4", status="closed", priority="low", assignee="user_3"),
        Ticket(id=5, title="Ticket 5", status="open", priority="medium", assignee="user_4"),
        ],
        "total_tickets": 5
    }

    # Call the /stats route (synchronously, since TestClient is synchronous)
    response = client.get("/stats")

    # Verify the response status code
    assert response.status_code == 200

    # Parse JSON response data
    data = response.json()

    # Check total number of tickets
    assert data["tickets"] == 5

    # Verify ticket counts by status
    assert data["status"]["open"] == 3  # 3 open tickets
    assert data["status"]["closed"] == 2  # 2 closed tickets

    # Verify ticket status percentages
    assert data["status_percent"]["open"] == 60.0  # 60% open tickets
    assert data["status_percent"]["closed"] == 40.0  # 40% closed tickets

    # Verify ticket counts by priority
    assert data["priority"]["low"] == 2  # 2 low priority tickets
    assert data["priority"]["medium"] == 2  # 2 medium priority tickets
    assert data["priority"]["high"] == 1  # 1 high priority ticket

    # Verify ticket priority percentages
    assert data["priority_percent"]["low"] == 40.0  # 40% low priority
    assert data["priority_percent"]["medium"] == 40.0  # 40% medium priority
    assert data["priority_percent"]["high"] == 20.0  # 20% high priority

    # Verify user statistics
    assert data["users"]["total"] == 5  # Total 5 users
    assert data["users"]["with_tickets"] == 4  # 4 users have tickets
    assert data["users"]["with_tickets_percent"] == 80.0  # 80% of users have tickets

    # Verify ticket statistics per user
    assert data["tickets_per_user"]["min"] == 1  # Minimum tickets per user
    assert data["tickets_per_user"]["max"] == 2  # Maximum tickets per user
    assert data["tickets_per_user"]["avg"] == 1.25  # Average tickets per user (rounded)

    # Verify user with the most tickets
    assert data["tickets_per_user"]["top_user"]["username"] == "user_1"  # User with the highest number of tickets
    assert data["tickets_per_user"]["top_user"]["tickets"] == 2  # Number of tickets of top user
