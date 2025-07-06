import httpx
from src.models.ticket_model import (
    Ticket,
    TicketStatus,
    TicketPriority,
    TicketWithRawResponse,
)
from fastapi import HTTPException
from src.config import TICKETS_URL, USERS_URL, CACHE_KEY_TICKETS, CACHE_TTL
from src.utils.exceptions import log_and_raise
from src.utils.logger import info, warning, error
from src.redis_cli import get_cache, set_cache, cache_exists


# Function to fetch tickets from the ecternal API
async def get_tickets() -> list[Ticket]:
    """
    Fetches tickets from an external API and returns a list of Ticket objects.
    This function retrieves tickets and their associated user information,
    mapping user IDs to usernames, and categorizing tickets by status and priority.
    Returns:
        A dictionary containing a list of Ticket objects and the total number of tickets.
    """
    cached_tickets = get_cache(CACHE_KEY_TICKETS)  # Get tickets from cache
    if cached_tickets:
        info("Returning cached tickets")
        tickets = [Ticket(**ticket) for ticket in cached_tickets]
        total_tickets = len(tickets)
        return {"tickets": tickets, "total_tickets": len(tickets)}
    try:
        async with httpx.AsyncClient() as client:
            # Fetch total number of tickets (limit=1 to get minimal data but total count)
            info("Fetching total number of todos...")
            total_todos_response = await client.get(TICKETS_URL, params={"limit": 1})
            total_todos = total_todos_response.json().get("total", 0)

            # Fetch total number of users (limit=1 to get minimal data but total count)
            info("Fetching total number of users...")
            total_users_response = await client.get(USERS_URL, params={"limit": 1})
            total_users = total_users_response.json().get("total", 0)

            # Fetch all todos and users with the total counts
            info("Fetching all todos and users...")
            todos_response = await client.get(
                TICKETS_URL, params={"limit": total_todos}
            )
            users_response = await client.get(USERS_URL, params={"limit": total_users})

            # Parse the JSON responses
            todos = todos_response.json()["todos"]
            users = users_response.json()["users"]

            # Create a mapping of user IDs to usernames for easy lookup
            users_map = {user["id"]: user["username"] for user in users}

            # Helper functions to map ticket priority and status
            def map_priority(ticket_id: int) -> TicketPriority:
                return ["low", "medium", "high"][ticket_id % 3]

            def map_status(completed: bool) -> TicketStatus:
                return TicketStatus.closed if completed else TicketStatus.open

            tickets = []

            # Iterate through todos and create Ticket objects
            for todo in todos:
                ticket = Ticket(
                    id=todo["id"],
                    title=todo["todo"],
                    status=map_status(todo["completed"]),
                    priority=map_priority(todo["id"]),
                    assignee=users_map.get(todo["userId"], "Unassigned"),
                )
                # Append the created ticket to the list
                tickets.append(ticket)
            info(f"Successfully mapped {len(tickets)} tickets.")

            set_cache(
                CACHE_KEY_TICKETS, [ticket.dict() for ticket in tickets], ttl=CACHE_TTL
            )
            info("Tickets data cached in Redis.")

            # Return the list of Ticket objects
            return {"tickets": tickets, "total_tickets": len(tickets)}

    except httpx.HTTPStatusError as e:
        # Log the HTTP error and raise an HTTPException
        log_and_raise(
            f"HTTP error while fetching tickets: {e}",
            status_code=e.response.status_code,
        )

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        # Log any unexpected errors and raise an HTTPException
        log_and_raise(f"Unexpected error in get_tickets: {e}")


# Function to fetch a specific ticket by ID and return it with raw response data
async def get_ticket_by_id(ticket_id: int) -> TicketWithRawResponse:
    """
    Fetches a ticket from an external API and returns a TicketWithRawResponse object.
    This function retrieves a ticket and its associated user information,
    mapping user IDs to usernames, and categorizing a ticket by status and priority.
    Returns:
        A TicketWithRawResponse object containing a Ticket object and todo raw dict.
    """
    cached_ticket = get_cache(f"ticket_{ticket_id}")
    cached_raw = get_cache(f"raw_{ticket_id}")
    if cached_ticket:
        # Return cached ticket if found
        info(f"Returning cached ticket with ID {ticket_id}")
        ticket = Ticket(**cached_ticket)
        raw = cached_raw

        return TicketWithRawResponse(ticket=ticket, raw=raw)

    try:
        async with httpx.AsyncClient() as client:
            # Fetch the todo item by ID
            info(f"Fetching ticket with ID: {ticket_id}")
            todo_response = await client.get(f"{TICKETS_URL}/{ticket_id}")

            if todo_response.status_code == 404:
                log_and_raise(f"Ticket with ID {ticket_id} not found", status_code=404)

            todo = todo_response.json()

            # Fetch the user associated with the todo item
            user_response = await client.get(f"{USERS_URL}/{todo['userId']}")
            username = user_response.json().get("username", "Unassigned")

            # Map the todo item to a Ticket object
            status = TicketStatus.closed if todo["completed"] else TicketStatus.open
            priority = ["low", "medium", "high"][todo["id"] % 3]

            # Create the Ticket object
            ticket = Ticket(
                id=todo["id"],
                title=todo["todo"],
                status=status,
                priority=priority,
                assignee=username,
            )

            # Create the TicketWithRawResponse object
            ticket_with_raw_response = TicketWithRawResponse(ticket=ticket, raw=todo)
            info(f"Successfully fetched ticket {ticket_id}")

            set_cache(f"ticket_{ticket_id}", ticket.dict(), ttl=CACHE_TTL)
            set_cache(f"raw_{ticket_id}", todo, ttl=CACHE_TTL)

            info(f"Ticket with ID {ticket_id} cached in Redis.")

            return ticket_with_raw_response

    except httpx.HTTPStatusError as e:
        # Log the HTTP error and raise an HTTPException
        if e.response.status_code == 404:
            log_and_raise(f"Ticket with ID {ticket_id} not found", status_code=404)
        else:
            log_and_raise(
                f"HTTP error while fetching ticket by ID {ticket_id}: {e}",
                status_code=e.response.status_code,
            )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        # Log any unexpected errors and raise an HTTPException
        log_and_raise(f"Unexpected error in get_ticket_by_id: {e}")
