SHELL=sh
MAIN=build-dev

BUILD=build

CONTAINER_IMAGE=category_api:latest

GREEN  := $(shell tput -Txterm setaf 2)
YELLOW := $(shell tput -Txterm setaf 3)
WHITE  := $(shell tput -Txterm setaf 7)
CYAN   := $(shell tput -Txterm setaf 6)
RESET  := $(shell tput -Txterm sgr0)

EXISTS_POETRY := $(shell command -v poetry 2> /dev/null)
EXISTS_FLASK := $(shell command -v uvicorn 2> /dev/null)

export CATEGORY_API_PORT ?= 28800
export CATEGORY_API_HOST ?= 0.0.0.0

export CATEGORY_API_START_TIME = $(shell date +%s)
export CATEGORY_API_GIT_COMMIT ?= $(shell git rev-parse HEAD)
export CATEGORY_API_VERSION ?= $(shell git tag --points-at HEAD | grep ^v | head -n 1)

ifneq (,$(wildcard ./.env))
	include .env
	export
endif

.PHONY: all audit audit-fix build build-bin delimiter deps fmt lint model run-container run test test-component test-unit help

all: delimiter-AUDIT audit delimiter-LINTERS lint delimiter-UNIT-TESTS test-unit delimiter-COMPONENT_TESTS test-component delimiter-FINISH ## Runs multiple targets, audit, lint, test and test-component

check-files:
	@if [ ! -f ./${BONN_CACHE_TARGET} ]; then echo "No cache file present"; exit 1; fi;
	@if [ ! -f ./${BONN_TAXONOMY_LOCATION} ]; then echo "No taxonomy file present"; exit 1; fi;
	@if [ ! -f ./${CATEGORY_API_FIFU_FILE} ]; then echo "No fifu file present"; exit 1; fi;

audit: deps ## Audits code for vulnerable dependencies
	poetry run pip-audit

audit-fix: deps ## Audits code for vulnerable dependencies and upgrades
	poetry run pip-audit --fix

build: ## Builds docker image - name: category_api:latest
	docker build -t category_api:latest .

build-bin: deps  ## Builds a wheel and a binary file
	poetry build

deps: ## Installs dependencies
	bash ./ci/scripts/deps.sh

delimiter-%:
	@echo '===================${GREEN} $* ${RESET}==================='

fmt: ## Formats code
	poetry run isort category_api
	poetry run black category_api

generate-envs: # generates an env file - warning, this will wipe your local .env file
	cp .env.local .env

lint: deps ## Lints code
	poetry run ruff check .

run: deps check-files ## Runs category api locally using poetry uvicorn port: 28800
	poetry run uvicorn category_api.main:app --host ${CATEGORY_API_HOST} --port ${CATEGORY_API_PORT}

run-container: deps build test_data/wiki.en.fifu check-files ## Builds docker container, downloads fifu data and then runs docker container
	docker run -e CATEGORY_API_GIT_COMMIT=${CATEGORY_API_GIT_COMMIT} -e CATEGORY_API_VERSION=${CATEGORY_API_VERSION} -e CATEGORY_API_START_TIME=${CATEGORY_API_START_TIME} --network=host category_api

test_data/wiki.en.fifu: ## Downloads/Updates fifu data inside the test_data dir
	curl -o test_data/wiki.en.fifu http://www.sfs.uni-tuebingen.de/a3-public-data/finalfusion-fasttext/wiki/wiki.en.fifu

test: deps unit test-component ## Makes sure deps are installed and runs all tests

test-component: deps ## Runs component tests
	poetry run pytest tests/api

unit: deps ## Runs unit tests
	poetry run pytest tests/unit

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

