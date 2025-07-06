import pytest
from fastapi.testclient import TestClient
from main import app

# Create a test client using the FastAPI app
client = TestClient(app)

def test_http_exception_handler(caplog):
    # Send a GET request to a non-existent endpoint to trigger a 404 error
    response = client.get("/non-existent-endpoint")
    
    # Assert that the response status code is 404 Not Found
    assert response.status_code == 404
    
    # Assert that the returned JSON contains the expected error detail
    assert response.json() == {"detail": "Not Found"}

    # Check the captured logs to verify that the custom error message was logged
    with caplog.at_level("ERROR"):
        assert "HTTP error: Not Found" in caplog.text
