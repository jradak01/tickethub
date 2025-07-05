from fastapi import APIRouter, Request, HTTPException
from src.services.ticket_service import get_tickets
from src.services.user_service import get_users_count
from src.models.ticket_model import TicketStatus, TicketPriority, Ticket
from collections import defaultdict
from statistics import mean
from src.utils.exceptions import log_and_raise
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter= Limiter(key_func=get_remote_address)

# Router for statistic endpoints
router = APIRouter()

# Endpoint to get statistics about tickets
@router.get("/stats")
@limiter.limit("10/minute")
async def get_stats(request: Request):
    # Fetch all tickets and user count
    try: 
        tickets_data = await get_tickets()
        num_users = await get_users_count()
    except HTTPException as e:
        raise e
    except Exception as e:
        log_and_raise(f"Unexpected error in get_stats: {e}", status_code=500)

    # Count total tickets 
    tickets = tickets_data["tickets"]
    total_tickets = tickets_data["total_tickets"]
    
    # Count tickets by status and priority
    open_tickets = sum(1 for t in tickets if t.status == TicketStatus.open)
    closed_tickets = total_tickets - open_tickets

    low_priority_tickets = sum(1 for t in tickets if t.priority== TicketPriority.low)
    medium_priority_tickets = sum(1 for t in tickets if t.priority == TicketPriority.medium)
    high_priority_tickets = sum(1 for t in tickets if t.priority == TicketPriority.high)

    # Count combinations of status and priority
    combo_stats = defaultdict(int)
    for t in tickets:
        key = f"{t.priority}_{t.status}"
        combo_stats[key] += 1
    
    # Find ticket with longest and shortest title and average number of characters in title
    if tickets:
        longest_title_ticket = max(tickets, key=lambda t: len(t.title))
        longest_title_length = len(longest_title_ticket.title)
        shortest_title_ticket = min(tickets, key=lambda t: len(t.title))
        shortest_title_length = len(shortest_title_ticket.title)
        avg_title_length = round(sum(len(t.title) for t in tickets) / total_tickets, 2)
    else:
        longest_title_ticket = None
        longest_title_length = 0
        shortest_title_ticket = None
        shortest_title_length = 0
        avg_title_length = 0

    # Count tickets per user
    tickets_per_user = defaultdict(int)
    for t in tickets:
        tickets_per_user[t.assignee] += 1 
    
    # Count users with tickets
    num_users_with_tickets = len(tickets_per_user)

    # Get counts of tickets per user
    counts = tickets_per_user.values()
    
    # Calculate min, max, and average tickets per user
    min_tickets = min(counts) if counts else 0
    max_tickets = max(counts) if counts else 0
    avg_tickets = mean(counts) if counts else 0
    
    # Calculate distribution of tickets per user
    distribution = distribution_per_user(tickets_per_user, max_tickets)
    
    # Find the user with the maximum tickets
    max_user = max(tickets_per_user, key=tickets_per_user.get) if tickets_per_user else None

    return {
        "tickets": total_tickets,
        "status":{
            "open": open_tickets,
            "closed": closed_tickets,
        },
        "status_percent":{
            "open": round(open_tickets / total_tickets * 100, 2) if total_tickets > 0 else 0,
            "closed": round(closed_tickets / total_tickets * 100, 2) if total_tickets > 0 else 0,
        },
        "priority": {
            "low": low_priority_tickets,
            "medium": medium_priority_tickets,
            "high": high_priority_tickets,
        },
        "priority_percent": {
            "low":    percentage(low_priority_tickets, total_tickets),
            "medium": percentage(medium_priority_tickets, total_tickets),
            "high":   percentage(high_priority_tickets, total_tickets),
        },
        "tickets_by_status_and_priority": dict(combo_stats),
        "title_length": {
            "longest_title": longest_title_ticket.title,
            "longest_title_len": longest_title_length,
            "shortest_title": shortest_title_ticket.title,
            "shortest_title_len": shortest_title_length,
            "avg_title_len": avg_title_length
        },
        "users": {
            "total": num_users,
            "with_tickets": num_users_with_tickets,
            "with_tickets_percent": percentage(num_users_with_tickets, num_users),
            },
        "tickets_per_user": {
            "min": min_tickets,
            "max": max_tickets,
            "avg": round(avg_tickets, 2),
            "ticket_distribution": distribution,
            "top_user": {
                "username": max_user,
                "tickets": max_tickets
            }
        },
    }

# Function to calculate percentage
def percentage(part: int, total: int) -> float:
    """Calculate percentage of part from total."""
    return round(part / total * 100, 2) if total > 0 else 0

# Function to calculate distribution of tickets per user
def distribution_per_user(tickets_per_user: dict[str, int], max_bucket: int) -> dict[str, int]:
    """Calculate distribution of tickets per user."""
    distribution = defaultdict(int)

    for user, count in tickets_per_user.items():
        if count > max_bucket:
            distribution[f"{max_bucket}+"] += 1
        else:
            distribution[count] += 1
    return dict(distribution)