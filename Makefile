# Makefile

IMAGE_NAME=nse-scraper
CONTAINER_NAME=nse-app
DOCKERFILE=Dockerfile.arm64v8

build:
	docker build -t $(IMAGE_NAME) -f $(DOCKERFILE) .
run:
	docker run --rm --name $(CONTAINER_NAME) --env-file .env $(IMAGE_NAME)
