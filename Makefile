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
restart-server:
	docker compose restart server

# Follow logs for all services
logs:
	docker compose logs -f

# Follow logs specifically for the server service
logs-server:
	docker compose logs -f server

# Local development targets
server-dev:
	cd server && uv run uvicorn main:app --reload --port 8000

web-dev:
	cd web && npm run dev

test-server:
	cd server && uv run pytest -v tests/

# Clean up unused Docker resources
clean:
	docker system prune -f
