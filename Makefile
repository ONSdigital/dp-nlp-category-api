SHELL=bash
MAIN=build

BUILD=build

.PHONY: all
all: build

.PHONY: wheels
wheels:
	@mkdir -p $(BUILD)/wheels
	docker build -t ff_fasttext_build -f Dockerfile.wheels .
	docker run --rm --entrypoint maturin -v $(shell pwd)/$(BUILD)/wheels:/app/build/target/wheels ff_fasttext_build build

.PHONY: build
build: Dockerfile
	docker-compose build

Dockerfile:
	m4 Dockerfile.in > Dockerfile

.PHONY: run
run: build
	docker-compose up
