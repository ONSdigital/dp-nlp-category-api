SHELL=sh
MAIN=build-dev

BUILD=build

CONTAINER_IMAGE=ff_fasttext_api:latest

GREEN  := $(shell tput -Txterm setaf 2)
YELLOW := $(shell tput -Txterm setaf 3)
WHITE  := $(shell tput -Txterm setaf 7)
CYAN   := $(shell tput -Txterm setaf 6)
RESET  := $(shell tput -Txterm sgr0)

EXISTS_POETRY := $(shell command -v poetry 2> /dev/null)
EXISTS_FLASK := $(shell command -v uvicorn 2> /dev/null)

.PHONY: all
all: build-dev

.PHONY: wheels
wheels:
	@mkdir -p $(BUILD)/wheels
	docker build -t ff_fasttext_build -f Dockerfile.wheels .
	docker run --rm --entrypoint maturin -v $(shell pwd)/$(BUILD)/wheels:/app/build/target/wheels ff_fasttext_build build

.PHONY: build
build: Dockerfile
	docker build -t ${CONTAINER_IMAGE} --no-cache .

.PHONY: build-dev
build-dev: Dockerfile
	docker-compose build

Dockerfile:
	m4 Dockerfile.in > Dockerfile

.PHONY: run
run: build-dev test_data/wiki.en.fifu
	docker-compose run -e FF_FASTTEXT_API_FIFU=wiki.en.fifu ff_fasttext_api

test_data/wiki.en.fifu:
	curl -o test_data/wiki.en.fifu http://www.sfs.uni-tuebingen.de/a3-public-data/finalfusion-fasttext/wiki/wiki.en.fifu

test_data/cc.cy.300.fifu:
	curl -o test_data/cc.cy.300.vec.gz https://dl.fbaipublicfiles.com/fasttext/vectors-crawl/cc.cy.300.vec.gz
	gunzip test_data/cc.cy.300.vec.gz
	@$(MAKE) model INPUT_VEC=test_data/cc.cy.300.vec OUTPUT_FIFU=test_data/cc.cy.300.fifu

cache/cache-cy.json:
	python translate_cache.py

.PHONY: run-cy
run-cy: build-dev test_data/cc.cy.300.fifu cache/cache-cy.json
	docker-compose run -e FF_FASTTEXT_CORE_REBUILD_CACHE=false -e FF_FASTTEXT_API_FIFU=wiki.cy.fifu -e FF_FASTTEXT_CORE_CACHE_TARGET=/app/cache/cache-cy.json ff_fasttext_api
	# Stopwords not yet available in Welsh: docker-compose run -e FF_FASTTEXT_CORE_STOPWORDS_LANGUAGE=welsh -e FF_FASTTEXT_API_FIFU=cc.cy.300.fifu ff_fasttext_api

.PHONY: model
model: build-dev
	docker-compose run -e RUST_BACKTRACE=1 --entrypoint poetry ff_fasttext_api run ffp-convert -f textdims ${INPUT_VEC} -t finalfusion ${OUTPUT_FIFU}

.PHONY: help
help: ## Show this help.
	@echo ''
	@echo 'Usage:'
	@echo '  ${YELLOW}make${RESET} ${GREEN}<target>${RESET}'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} { \
		if (/^[a-zA-Z_-]+:.*?##.*$$/) {printf "    ${YELLOW}%-20s${GREEN}%s${RESET}\n", $$1, $$2} \
		else if (/^## .*$$/) {printf "  ${CYAN}%s${RESET}\n", substr($$1,4)} \
		}' $(MAKEFILE_LIST)

.PHONY: deps
deps:
	@if [ -z "$(EXISTS_FLASK)" ]; then \
	if [ -z "$(EXISTS_POETRY)" ]; then \
		pip -qq install poetry; \
		poetry config virtualenvs.in-project true; \
	fi; \
		poetry install --quiet || poetry install; \
	fi; \

.PHONY: test-component
test-component: deps
	poetry run pytest tests/api

.PHONY: unit
unit: deps
	poetry run pytest tests/unit

.PHONY: test
test: unit test-component

.PHONY: fmt
fmt: deps
	poetry run isort ff_fasttext_api
	poetry run black ff_fasttext_api

.PHONY: lint
lint: deps
	poetry run pflake8 ff_fasttext_api
	poetry run black --check ff_fasttext_api

.PHONY: audit
audit: deps
	poetry run jake ddt --whitelist ci/audit-allow-list.json
