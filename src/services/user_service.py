import httpx
from fastapi import HTTPException
from src.config import USERS_URL


# Function to fetch a total number of users
async def get_users_count() -> int:
    """
        Fetches users from an external API and returns a int.
        This function retrieves users and calculates the total number of users.
    """
    async with httpx.AsyncClient() as client:
        # Fetch total number of tickets
        total_users_response = await client.get(USERS_URL, params={"limit": 1})
        total_users = total_users_response.json()
        
        total = total_users.get("total", 0)
        
        
        return total