from fastapi import APIRouter
from typing import Optional
from src.services.ticket_service import get_tickets
from src.models.ticket_model import (Ticket, TicketSummary, 
                                     TicketListResponse, TicketWithRawResponse, 
                                     TicketStatus, TicketPriority)

# Router for ticket-related endpoints
router = APIRouter()


# Endpoint to get all tickets
@router.get("/tickets", response_model=TicketListResponse)
async def get_all_tickets():
    ticket_data = await get_tickets()
    tickets = ticket_data["tickets"]
    
    summaries = [
        TicketSummary(
            id=t.id,
            title=t.title,
            status=t.status,
            priority=t.priority,
            description=t.title[:100]
        )
        for t in tickets
    ]
    
    return TicketListResponse(
        total_tickets=len(summaries),
        tickets=summaries
    )