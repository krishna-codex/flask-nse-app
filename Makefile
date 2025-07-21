# Makefile for building and running NSE web scraper with Docker

IMAGE_NAME = nse-scraper
CONTAINER_NAME = nse-scraper-container
ENV_FILE = .env

# Build the Docker image
build:
	docker build -t $(IMAGE_NAME) .

# Run the container with .env variables
run:
	docker run --rm --name $(CONTAINER_NAME) --env-file $(ENV_FILE) $(IMAGE_NAME)

# Clean Docker image and container
clean:
	docker rm -f $(CONTAINER_NAME) 2>/dev/null || true
	docker rmi -f $(IMAGE_NAME) 2>/dev/null || true
	@echo "🧹 Cleaned Docker image and container."

# Show help
help:
	@echo ""
	@echo "📦 NSE Scraper Makefile Commands:"
	@echo "  make build     - Build the Docker image"
	@echo "  make run       - Run the script in Docker (with .env)"
	@echo "  make clean     - Remove image and container"
	@echo ""