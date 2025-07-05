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
    page_size: int = Query(10, ge=1, le=100)
):
    ticket_data = await get_tickets()
    tickets = ticket_data["tickets"]
    
    start = (page - 1) * page_size
    end = start + page_size
    page_tickets = tickets[start:end] 
    
    summaries = [
        TicketSummary(
            id=t.id,
            title=t.title,
            status=t.status,
            priority=t.priority
        )
        for t in page_tickets
    ]
    
    return TicketListResponse(
        total_tickets=len(tickets),
        tickets=summaries,
        page = page,
        page_size = page_size
    )