import httpx
from src.models.ticket import Ticket, TicketStatus, TicketPriority, TicketWithRawResponse
from fastapi import HTTPException
from src.config import TICKETS_URL, USERS_URL

# Function to fetch tickets from the ecternal API
async def get_tickets() -> list[Ticket]:
    """
        Fetches tickets from an external API and returns a list of Ticket objects.
        This function retrieves tickets and their associated user information,
        mapping user IDs to usernames, and categorizing tickets by status and priority.
        Returns:
            A dictionary containing a list of Ticket objects and the total number of tickets.
    """
    async with httpx.AsyncClient() as client:
        # Fetch total number of tickets (limit=1 to get minimal data but total count)
        total_todos_response = await client.get(TICKETS_URL, params={"limit": 1})
        total_todos = total_todos_response.json().get("total", 0)
        
        # Fetch total number of users (limit=1 to get minimal data but total count)
        total_users_response = await client.get(USERS_URL, params={"limit": 1})
        total_users = total_users_response.json().get("total", 0)    
        # Fetch all todos and users with the total counts
        todos_response = await client.get(TICKETS_URL, params={"limit": total_todos})
        users_response = await client.get(USERS_URL, params={"limit": total_users})
        # Parse the JSON responses
        todos = todos_response.json()["todos"]
        users= users_response.json()["users"]
        # Create a mapping of user IDs to usernames for easy lookup
        users_map= {user["id"]: user["username"] for user in users}
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
                title = todo["todo"],
                status = map_status(todo["completed"]),
                priority = map_priority(todo["id"]),
                assignee = users_map.get(todo["userId"], "Unassigned")
            )
            # Append the created ticket to the list
            tickets.append(ticket)
        
        # Return the list of Ticket objects
        return {
            "tickets": tickets,
            "total_tickets": len(tickets)
        }