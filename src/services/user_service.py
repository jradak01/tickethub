import httpx
from fastapi import HTTPException
from src.config import USERS_URL
from src.utils.exceptions import log_and_raise

# Function to fetch a total number of users
async def get_users_count() -> int:
    """
        Fetches users from an external API and returns a int.
        This function retrieves users and calculates the total number of users.
    """
    try:
        async with httpx.AsyncClient() as client:
            # Fetch total number of tickets
            total_users_response = await client.get(USERS_URL, params={"limit": 1})
            total_users = total_users_response.json()

            total = total_users.get("total", 0)


            return total
        
    except httpx.HTTPStatusError as e:
        log_and_raise("HTTP error while fetching user count", status_code=e.response.status_code)

    except Exception as e:
        log_and_raise(f"Unexpected error in get_users_count: {e}")