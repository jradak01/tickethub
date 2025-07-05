from fastapi import APIRouter, Query, Request
from typing import Optional
from src.services.ticket_service import get_tickets
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