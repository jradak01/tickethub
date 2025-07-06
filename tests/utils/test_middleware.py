import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_request_info_logging(caplog):
    # Enable INFO level logging
    with caplog.at_level("INFO"): 
        # Make a GET request to the root endpoint
        response = client.get("/")

    # Check if the response was successful
    assert response.status_code == 200
    
    # Check if request method, path, and body were logged correctly
    assert "Method: GET" in caplog.text
    assert "Path: http://testserver/" in caplog.text
    assert "Body: No body" in caplog.text
