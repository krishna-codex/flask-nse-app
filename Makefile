IMAGE_NAME = nse-scraper
DOCKERFILE = Dockerfile.arm64v8
TAG = latest

build:
	docker build -t $(IMAGE_NAME):$(TAG) -f $(DOCKERFILE) .
run:
	docker run --rm --env-file .env $(IMAGE_NAME):$(TAG)
clean:
	docker rmi -f $(IMAGE_NAME):$(TAG)
clean-all:
	docker rmi -f $$(docker images -q)
