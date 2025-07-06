from fastapi import APIRouter, Query, Request, HTTPException
from typing import Optional
from src.services.ticket_service import get_tickets, get_ticket_by_id
from src.models.ticket_model import (
    Ticket,
    TicketSummary,
    TicketListResponse,
    TicketWithRawResponse,
    TicketStatus,
    TicketPriority,
)
from src.utils.logger import error
from src.utils.exceptions import log_and_raise
from slowapi import Limiter
from slowapi.util import get_remote_address


limiter = Limiter(key_func=get_remote_address)

# Router for ticket-related endpoints
router = APIRouter()


# Endpoint to get all tickets
@router.get("/tickets", response_model=TicketListResponse)
@limiter.limit("10/minute")
async def get_all_tickets(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[TicketStatus] = Query(None),
    priority: Optional[TicketPriority] = Query(None),
):
    # Fetch tickets from the service
    try:
        ticket_data = await get_tickets()
    except HTTPException as e:
        raise e
    except Exception as e:
        log_and_raise(f"Unexpected error in get_all_tickets: {e}", status_code=500)
    tickets = ticket_data["tickets"]

    # Calculate pagination parameters
    start = (skip - 1) * skip
    end = start + limit

    # Filter tickets by status and priority if provided
    if status:
        tickets = [t for t in tickets if t.status == status]
    if priority:
        tickets = [t for t in tickets if t.priority == priority]

    # Apply pagination
    page_tickets = tickets[start:end]

    # Create summaries for the tickets in the current page
    summaries = [
        TicketSummary(id=t.id, title=t.title, status=t.status, priority=t.priority)
        for t in page_tickets
    ]

    # Return the paginated response
    return TicketListResponse(
        total_tickets=len(tickets), tickets=summaries, skip=skip, limit=limit
    )


# Endpoint to search tickets by title
@router.get("/tickets/search", response_model=list[Ticket])
@limiter.limit("20/minute")
async def search_tickets(request: Request, q: str = Query(..., min_length=1)):

    # Fetch all tickets from the service
    try:
        tickets = await get_tickets()
    except HTTPException as e:
        raise e
    except Exception as e:
        log_and_raise(f"Unexpected error in search_tickets: {e}", status_code=500)
        error("Unexpected error in search_tickets:", str(e))

    # Filter tickets by title containing the search query (case insensitive)
    filtered = [t for t in tickets["tickets"] if q.lower() in t.title.lower()]
    return filtered


# Endpoint to get a specific ticket by ID
@router.get("/tickets/{ticket_id}", response_model=TicketWithRawResponse)
@limiter.limit("20/minute")
async def get_ticket(request: Request, ticket_id: int):
    # Fetch ticket from the service
    try:
        ticket = await get_ticket_by_id(ticket_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        log_and_raise(f"Unexpected error in get_ticket: {e}", status_code=500)
        error("Unexpected error in get_ticket:", str(e))

    return ticket
