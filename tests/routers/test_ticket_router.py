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

@pytest.mark.asyncio
async def test_get_all_tickets(mock_get_tickets):
    # Mock the response of the get_tickets function to return a list of ticket data
    mock_get_tickets.return_value = {"tickets":[
        Ticket(
            id= 1,
            title= "Ticket 1",
            status= "open",
            priority= "medium",
            assignee= "user1"
        ),Ticket(
            id= 2,
            title= "Ticket 2",
            status= "closed",
            priority= "high",
            assignee= "user2"
        )
    ],
    "total_tickets":2
    }

    # Create a TestClient instance for testing the app
    client = TestClient(app)
    
    # Send a GET request to the /tickets route with query parameters 'limit' and 'skip'
    response = client.get("/tickets?limit=2&skip=0")

    # Check the response status code to ensure the request was successful
    assert response.status_code == 200
    
    # Verify that the response contains 2 tickets (as specified by 'limit=2')
    assert len(response.json()["tickets"]) == 2
    
    # Check the content of the first ticket in the response
    assert response.json()["tickets"][0]["id"] == 1
    
    # Check the status of the second ticket to ensure it matches the expected value
    assert response.json()["tickets"][1]["status"] == "closed"
    
@pytest.mark.asyncio
async def test_get_all_tickets_no_filter(mock_get_tickets):
    # Mock the response for the get_tickets function to return a list of tickets with no filters applied
    mock_get_tickets.return_value = {"tickets":[
        Ticket(
            id=1,
            title="Ticket 1",
            status="open",
            priority="medium",
            assignee="user1"
        )],
        "total_tickerts": 1
        }

    # Create a TestClient instance to simulate requests to the app
    client = TestClient(app)
    
    # Send a GET request to the /tickets route without any filters (e.g., no limit or skip)
    response = client.get("/tickets")

    # Check the response status code to ensure the request was successful
    assert response.status_code == 200
    
    # Verify that the response contains exactly one ticket
    assert len(response.json()["tickets"]) == 1
    
    # Check the ID of the returned ticket to ensure it matches the expected value
    assert response.json()["tickets"][0]["id"] == 1

# Testing the /tickets/search route to ensure it correctly filters tickets based on the search query parameter
@pytest.mark.asyncio
async def test_search_tickets(mock_get_tickets):
    # Mock the response for get_tickets to return a list of Ticket objects with different titles
    mock_get_tickets.return_value = {"tickets":[
        Ticket(
            id=1,
            title="Do something nice for someone",
            status="open",
            priority="medium",
            assignee="paisleyf"
        ),
        Ticket(
            id=2,
            title="Ticket to the moon",
            status="closed",
            priority="high",
            assignee="moonwalker"
        )
    ],
    "total_tickets": 2}

    # Create a TestClient instance to simulate requests to the app
    client = TestClient(app)
    
    # Send a GET request to the /tickets/search route with a query parameter 'q=moon'
    response = client.get("/tickets/search?q=moon")
    response_json = response.json()

    # Print the full response for debugging purposes (can be removed later)
    print(response_json)

    # Check the response status code to ensure the request was successful
    assert response.status_code == 200
    
    # Verify that the response contains exactly one ticket that matches the search query
    assert len(response_json) == 1
    
    # Check that the title of the returned ticket matches the expected value
    assert response_json[0]["title"] == "Ticket to the moon"


# Testing the /tickets route to ensure it correctly filters tickets based on the provided query parameters
@pytest.mark.asyncio
async def test_search_tickets_with_filters(mock_get_tickets):
    # Mock the response for get_tickets to return a list of Ticket objects with different statuses and priorities
    mock_get_tickets.return_value = {"tickets":[
            Ticket(
                id=1,
                title="Ticket 1",
                status="open",
                priority="medium",
                assignee="user1"
            ),
            Ticket(
                id=2,
                title="Ticket 2",
                status="closed",
                priority="high",
                assignee="user2"
            ),
            Ticket(
                id=3,
                title="Ticket 3",
                status="open",
                priority="low",
                assignee="user3"
            )
        ],
        "total_tickets": 3
    }

    # Create a TestClient instance to simulate requests to the app
    client = TestClient(app)

    # Send a GET request to /tickets with filters for status "open" and priority "medium"
    response = client.get("/tickets", params={"status": "open", "priority": "medium"})

    # Check the status and the number of filtered responses
    assert response.status_code == 200
    assert len(response.json()["tickets"]) == 1
    assert response.json()["tickets"][0]["id"] == 1
    assert response.json()["tickets"][0]["status"] == "open"
    assert response.json()["tickets"][0]["priority"] == "medium"

    # Filter by status "closed"
    response = client.get("/tickets", params={"status": "closed"})
    
    # Check the status for the "closed" ticket
    assert response.status_code == 200
    assert len(response.json()["tickets"]) == 1
    assert response.json()["tickets"][0]["id"] == 2
    assert response.json()["tickets"][0]["status"] == "closed"
