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
