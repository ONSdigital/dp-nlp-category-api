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

export FF_FASTTEXT_API_CATEGORY_API_PORT ?= 28800
export FF_FASTTEXT_API_CATEGORY_API_HOST ?= 0.0.0.0

export FF_FASTTEXT_API_START_TIME = $(shell date +%s)
export FF_FASTTEXT_API_GIT_COMMIT ?= $(shell git rev-parse HEAD)
export FF_FASTTEXT_API_VERSION ?= $(shell git tag --points-at HEAD | grep ^v | head -n 1)


.PHONY: all audit build build-bin build-dev deps delimiter fmt lint model run-container run test test-component test-unit help

all: delimiter-AUDIT audit delimiter-LINTERS lint delimiter-UNIT-TESTS test-unit delimiter-COMPONENT_TESTS test-component delimiter-FINISH ## Runs multiple targets, audit, lint, test and test-component

audit: deps ## Makes sure dep are installed and audits code for vulnerable dependencies
	poetry run safety check

build: Dockerfile ## Creates a Dockerfile from Dockerfile.in if non exists, then builds docker image - name: ff_fasttext_api:latest
	docker build -t ${CONTAINER_IMAGE} .

build-bin: deps  ## Builds a binary file called 
	poetry build

build-dev: Dockerfile ## Runs docker-compose build
	docker-compose build

cache/cache-cy.json:
	python translate_cache.py

deps: ## Installs dependencies
	@if [ -z "$(EXISTS_FLASK)" ]; then \
	if [ -z "$(EXISTS_POETRY)" ]; then \
		pip -qq install poetry; \
		poetry config virtualenvs.in-project true; \
	fi; \
		poetry install --quiet || poetry install; \
	fi; \

Dockerfile: ## Creates a dockerfile from Dockerfile.in using m4 (m4 must be installed)
	m4 Dockerfile.in > Dockerfile

delimiter-%:
	@echo '===================${GREEN} $* ${RESET}==================='

fmt: deps ## Makes sure dep are installed and formats code
	poetry run isort ff_fasttext_api
	poetry run black ff_fasttext_api

lint: deps ## Makes sure dep are installed and lints code
	poetry run ruff check .

model: build-dev
	docker-compose run -e RUST_BACKTRACE=1 --entrypoint poetry ff_fasttext_api run ffp-convert -f textdims ${INPUT_VEC} -t finalfusion ${OUTPUT_FIFU}

run: ## Runs category api locally using poetry uvicorn port: 28800
	poetry run uvicorn api:app --host ${FF_FASTTEXT_API_CATEGORY_API_HOST} --port ${FF_FASTTEXT_API_CATEGORY_API_PORT}

run-container: build test_data/wiki.en.fifu ## Builds docker container, downloads fifu data and then runs docker container
	docker run --network=host ff_fasttext_api

test_data/wiki.en.fifu: ## Downloads/Updates fifu data inside the test_data dir
	curl -o test_data/wiki.en.fifu http://www.sfs.uni-tuebingen.de/a3-public-data/finalfusion-fasttext/wiki/wiki.en.fifu

test_data/cc.cy.300.fifu: ## Downloads/Updates cc.cy.300.fifu data inside test_data dir
	curl -o test_data/cc.cy.300.vec.gz https://dl.fbaipublicfiles.com/fasttext/vectors-crawl/cc.cy.300.vec.gz
	gunzip test_data/cc.cy.300.vec.gz
	@$(MAKE) model INPUT_VEC=test_data/cc.cy.300.vec OUTPUT_FIFU=test_data/cc.cy.300.fifu

test: unit test-component ## Makes sure dep are installed and runs all tests

test-component: deps ## Makes sure dep are installed and runs component tests
	poetry run pytest tests/api

unit: deps ## Makes sure dep are installed and runs unit tests
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

