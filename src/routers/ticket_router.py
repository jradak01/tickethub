from fastapi import APIRouter, Query, Request
from typing import Optional
from src.services.ticket_service import get_tickets, get_ticket_by_id
from src.models.ticket_model import (Ticket, TicketSummary, 
                                     TicketListResponse, TicketWithRawResponse, 
                                     TicketStatus, TicketPriority)

# Router for ticket-related endpoints
router = APIRouter()


# Endpoint to get all tickets
@router.get("/tickets", response_model=TicketListResponse)
async def get_all_tickets(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: Optional[TicketStatus] = Query(None),
    priority: Optional[TicketPriority] = Query(None)
):
    # Fetch tickets from the service
    ticket_data = await get_tickets()
    tickets = ticket_data["tickets"]
    
    # Calculate pagination parameters
    start = (page - 1) * page_size
    end = start + page_size
    
    # Filter tickets by status and priority if provided
    if status:
        tickets = [t for t in tickets if t.status == status]
    if priority:
        tickets = [t for t in tickets if t.priority == priority]

    # Apply pagination
    page_tickets = tickets[start:end] 

    # Create summaries for the tickets in the current page
    summaries = [
        TicketSummary(
            id=t.id,
            title=t.title,
            status=t.status,
            priority=t.priority
        )
        for t in page_tickets
    ]
    
    # Return the paginated response
    return TicketListResponse(
        total_tickets=len(tickets),
        tickets=summaries,
        page = page,
        page_size = page_size
    )


# Endpoint to search tickets by title
@router.get("/tickets/search", response_model=list[Ticket]) 
async def search_tickets(
    request: Request,
    q: str = Query(..., min_length=1)):
    
    # Fetch all tickets from the service
    tickets = await get_tickets()
        
    # Filter tickets by title containing the search query (case insensitive)
    filtered = [t for t in tickets["tickets"] if q.lower() in t.title.lower()]
    return filtered

# Endpoint to get a specific ticket by ID
@router.get("/tickets/{ticket_id}", response_model=TicketWithRawResponse)
async def get_ticket(
    request: Request,
    ticket_id: int):
    # Fetch ticket from the service
    ticket = await get_ticket_by_id(ticket_id)

    return ticket