# TicketHub - Middleware Service for Support Tickets

## Overview

TicketHub is a RESTful service built with FastAPI that interacts with the DummyJSON API to manage and expose support tickets. It fetches tickets, processes them, and allows querying through various endpoints. Additionally, it includes endpoints for statistics and user authentication.

## Features Implemented:

**Ticket Retrieval**: Fetch tickets from the DummyJSON API and transform them into a custom model.

**Ticket Management:**

- Pagination for listing tickets.

- Detailed view of a single ticket.

- Filtering by status and priority.

- Search functionality for ticket titles.

**Statistics:** View aggregated statistics about tickets through the /stats endpoint.

**Authentication:** User login via JWT at the /auth/login endpoint.

**Caching with Redis:** Implement Redis for caching ticket data and improving performance.

**Rate Limiting with SlowAPI:** Protect the application from excessive requests using rate limiting.

**Logging:** Logs requests and errors at various levels (INFO, WARNING, ERROR).

**Dockerized Setup:** The project is containerized using Docker.

---

## How to run the project

### 1. Clone the repository

```
git clone https://github.com/jradak01/tickethub.git
cd tickethub
```

### 2. Set Up the Environment

Create a virtual environment and activate it:

```
python3 -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\Activate.ps1`
```

Install dependencies:

```
pip install -r requirements.txt
```

### 3. Running the Application
To start the app with Docker Compose:

```
docker-compose up --build
```

This will build and start the FastAPI app, along with Redis for caching.

To run the app without Docker:

```
uvicorn main:app --reload
Access the app at http://localhost:8000.
```

## Endpoints

1. **GET /tickets**

Retrieve a paginated list of tickets.

Example request:

```
GET /tickets?page=1&limit=10
```

2. **GET /tickets/{id}**

Get the detailed information for a specific ticket.

Example request:

```
GET /tickets/1
```

3. **GET /tickets?status=<status>&priority=<priority>**

Filter tickets by status and priority.

Example request:

```
GET /tickets?status=open&priority=medium
```

4. **GET /tickets/search?q=<query>**

Search tickets by title.

Example request:

```
GET /tickets/search?q=payment
```

5. **GET /stats**

View aggregated statistics about tickets, such as the number of tickets by status or priority.

6. **POST /auth/login**

User login endpoint, returns a JWT for authentication.

Example request:

```
POST /auth/login
```

## Rate Limiting with SlowAPI

To protect the application from excessive requests and avoid abuse, SlowAPI is integrated for rate limiting. It limits the number of requests a user can make within a specified time frame.

## Testing

To run tests:

```
make test
```

or

```
$env:PYTHONPATH="."; pytest -v
```

Tests are implemented using pytest.

## Makefile Commands

Run the application: ```make run```

Run the tests: ```make test```

Stop the containers: ```make stop```

Clean Docker resources: ```make clean```

## Docker Setup

**Dockerfile**
The project includes a Dockerfile to containerize the FastAPI application. It installs all the necessary dependencies and prepares the environment for running the app.

**docker-compose.yml**
The docker-compose.yml file is used to manage multi-container environments. It includes services for:

- The FastAPI app

- Redis (for caching)

**Running with Docker Compose**

To build and start the application with Docker Compose:

```
docker-compose up --build
```