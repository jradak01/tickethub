import httpx
from fastapi import HTTPException
from src.config import USERS_URL, CACHE_TTL, CACHE_KEY_USERS
from src.utils.logger import info, warning, error
from src.utils.exceptions import log_and_raise
from src.redis_cli import get_cache, set_cache, cache_exists


# Function to fetch a total number of users
async def get_users_count() -> int:
    """
    Fetches users from an external API and returns a int.
    This function retrieves users and calculates the total number of users.
    """
    cached_user_count = get_cache(CACHE_KEY_USERS)  # Get tickets from cache
    if cached_user_count:
        info("Returning cached users count")
        return int(cached_user_count)
    try:
        async with httpx.AsyncClient() as client:
            # Fetch total number of tickets
            info("Fetching users count from API...")
            total_users_response = await client.get(USERS_URL, params={"limit": 1})
            total_users = total_users_response.json()

            total = total_users.get("total", 0)

            set_cache(CACHE_KEY_USERS, total, ttl=CACHE_TTL)
            info("Users count cached in Redis.")

            return total

    except httpx.HTTPStatusError as e:
        log_and_raise(
            "HTTP error while fetching user count", status_code=e.response.status_code
        )

    except Exception as e:
        log_and_raise(f"Unexpected error in get_users_count: {e}")
