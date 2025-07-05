# Using Python 3.11 as the base image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Set the Python path to the working directory
ENV PYTHONPATH=/app

# Copy requirements.txt into the container
COPY requirements.txt .

# Install the required dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the working directory in the container
COPY . .

# Expose the port that the application will use
EXPOSE 8000

# Run the application using the FastAPI ASGI format (always use ASGI for FastAPI)
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
