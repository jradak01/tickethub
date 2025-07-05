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