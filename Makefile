

IMAGE_NAME=nse-app
DOCKERFILE=Dockerfile.arm64v8

build:
	docker build -f $(DOCKERFILE) -t $(IMAGE_NAME) .


rebuild: clean build run

clean:
	docker rmi -f $(IMAGE_NAME) || true

