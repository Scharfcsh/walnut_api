.PHONY: build up down logs test clean

# Build and start services
build:
	docker-compose build

# Start all services
up:
	docker-compose up -d

# Stop all services  
down:
	docker-compose down

# View logs
logs:
	docker-compose logs -f

# Run requirements test
test:
	python test_requirements.py

# Clean up
clean:
	docker-compose down -v
	docker system prune -f

# Development setup
dev-setup:
	cp .env.example .env
	echo "Update .env with your configuration"

# Check service status
status:
	docker-compose ps
	curl -s http://localhost:8000/ | jq .
