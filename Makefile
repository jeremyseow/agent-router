# Docker lifecycle management for Agent Router

.PHONY: build up down restart logs clean

# Build the application image
build:
	docker compose build

# Start all services in the background
up:
	docker compose up -d

# Stop and remove all containers
down:
	docker compose down

# Restart the application service
restart-app:
	docker compose restart app

# Follow logs for all services
logs:
	docker compose logs -f

# Follow logs specifically for the app service
logs-app:
	docker compose logs -f app

# Clean up unused Docker resources
clean:
	docker system prune -f
