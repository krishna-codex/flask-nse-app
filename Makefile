# Makefile for building and running the Docker container

IMAGE_NAME = nse_app

build:
	docker build -t nse-app .


clean:
	docker rmi $(IMAGE_NAME)

.PHONY: build run clean