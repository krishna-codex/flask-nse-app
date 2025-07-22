APP_NAME=nse-app
IMAGE_NAME=nse-scraper

.PHONY: build run clean shell

build:
	docker build -t $(IMAGE_NAME) .

clean:
	-docker rm -f $(APP_NAME)
	-docker rmi -f $(IMAGE_NAME)
