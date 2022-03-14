SHELL=sh
MAIN=build-dev

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
	docker build -t ${CONTAINER_IMAGE} -t ${IMAGE_LATEST_TAG} -t ${IMAGE_SHA_TAG} .

.PHONY: build-dev
build-dev: Dockerfile
	docker-compose build-dev

Dockerfile:
	m4 Dockerfile.in > Dockerfile

.PHONY: run
run: build-dev
	docker-compose up
