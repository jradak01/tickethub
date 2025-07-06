# Define variables
DOCKER_COMPOSE=docker-compose

# Run the application (build and up)
run:
	@echo "Starting the application..."
	$(DOCKER_COMPOSE) up --build

# Run tests
test:
	@echo "Running tests..."
	$(DOCKER_COMPOSE) run --rm test

# Stop the containers
stop:
	@echo "Stopping containers..."
	$(DOCKER_COMPOSE) down

# Clean Docker images (if you want to delete them)
clean:
	@echo "Cleaning Docker images..."
	docker system prune -f

.PHONY: run test stop clean
