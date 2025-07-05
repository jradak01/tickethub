import httpx
from fastapi import HTTPException
from src.models.auth_model import LoginRequest
from src.config import AUTH_URL

# Function to authenticate user
async def authenticate_user(login_data):
    """
        Authenticates a user by sending login credentials to an external authentication service.
        This function sends a POST request with the user's login data, handles various HTTP errors,
        and extracts the access and refresh tokens along with the username from the response.
    
        Args:
            login_data (LoginRequest): The user's login credentials.

        Returns:
            dict: A dictionary containing "access_token", "refresh_token", and "username".
    """
    async with httpx.AsyncClient() as client:
        try:
            # Send POST request to authentication URL with login data as JSON
            response = await client.post(AUTH_URL, json=login_data.dict())

            # Handle specific HTTP error status codes with custom messages
            if response.status_code == 400:
                raise HTTPException(status_code=400, detail="Invalid credentials")
            
            elif response.status_code == 401:
                raise HTTPException(status_code=401, detail="Unauthorized")

            elif response.status_code >= 500:
                raise HTTPException(status_code=500, detail="Server error")

            # Raise exception for any other unsuccessful HTTP status codes
            response.raise_for_status() 
            
        except httpx.HTTPStatusError as e:
            # Handle unexpected HTTP errors from the authentication server
            raise HTTPException(status_code=500, detail="Unexpected authentication error")
        
        except httpx.RequestError as e:
            # Handle network-related errors such as connection problems
            raise HTTPException(status_code=503, detail="Authentication service unavailable")
        
        # Parse the JSON response content
        data = response.json()

        # Verify that the response contains an access token
        if "accessToken" not in data:
            raise HTTPException(status_code=500, detail="Token not found in response")

        # Return the tokens and username extracted from the response
        return {
            "access_token": data["accessToken"],
            "refresh_token": data["refreshToken"],
            "username": data["username"]
        }