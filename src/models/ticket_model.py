from pydantic import BaseModel
from enum import Enum
from typing import Any

# Ticket status enum - limits allowed values to "open" or "closed"
class TicketStatus(str, Enum):
    open = "open"
    closed = "closed"

# Ticket priority enum - limits allowed values to "low", "medium", or "high"
class TicketPriority(str, Enum):
    low= "low"
    medium = "medium"
    high = "high"

# Ticket model - defines the structure of a ticket object
class Ticket(BaseModel):
    id: int
    title: str
    status: TicketStatus
    priority: TicketPriority
    assignee: str

# TicketWithRawResponse model - includes a ticket and its raw response data
class TicketWithRawResponse(BaseModel):
    ticket: Ticket
    raw: dict[str, Any]