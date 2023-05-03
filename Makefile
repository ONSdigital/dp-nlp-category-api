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
all: build ## 

.PHONY: audit
audit: deps ## Makes sure dep are installed and audits code for vulnerable dependencies
	pip install safety
	safety check

.PHONY: build
build: Dockerfile ## Creates a Dockerfile from Dockerfile.in if non exists, then builds docker image - name: ff_fasttext_api:latest
	docker build -t ${CONTAINER_IMAGE} .

.PHONY: build-bin
build-bin: deps  ## Builds a binary file called 
	poetry build

.PHONY: build-dev
build-dev: Dockerfile ## Runs docker-compose build
	docker-compose build

Dockerfile: ## Creates a dockerfile from Dockerfile.in using m4 (m4 must be installed)
	m4 Dockerfile.in > Dockerfile

.PHONY: run_dc 
run_dc: build-dev test_data/wiki.en.fifu ## Builds docker-compose, downloads fifu data and then runs docker-compose up 
	docker-compose run -e FF_FASTTEXT_API_FIFU=wiki.en.fifu ff_fasttext_api

.PHONY: run_container 
run_container: build test_data/wiki.en.fifu ## Builds docker container, downloads fifu data and then runs docker container
	docker run --network=host ff_fasttext_api

.PHONY: run-cy 
run-cy: build-dev test_data/cc.cy.300.fifu cache/cache-cy.json ## 
	docker-compose run -e FF_FASTTEXT_CORE_REBUILD_CACHE=false -e FF_FASTTEXT_API_FIFU=wiki.cy.fifu -e FF_FASTTEXT_CORE_CACHE_TARGET=/app/cache/cache-cy.json ff_fasttext_api
	# Stopwords not yet available in Welsh: docker-compose run -e FF_FASTTEXT_CORE_STOPWORDS_LANGUAGE=welsh -e FF_FASTTEXT_API_FIFU=cc.cy.300.fifu ff_fasttext_api

.PHONY: run_local
run_local: ## Runs category api locally using poetry uvicorn port: 3003
	poetry run uvicorn ff_fasttext_api.server:create_app --host 0.0.0.0 --port 3003

test_data/wiki.en.fifu: ## Downloads/Updates fifu data inside the test_data dir
	curl -o test_data/wiki.en.fifu http://www.sfs.uni-tuebingen.de/a3-public-data/finalfusion-fasttext/wiki/wiki.en.fifu

test_data/cc.cy.300.fifu: ## Downloads/Updates cc.cy.300.fifu data inside test_data dir
	curl -o test_data/cc.cy.300.vec.gz https://dl.fbaipublicfiles.com/fasttext/vectors-crawl/cc.cy.300.vec.gz
	gunzip test_data/cc.cy.300.vec.gz
	@$(MAKE) model INPUT_VEC=test_data/cc.cy.300.vec OUTPUT_FIFU=test_data/cc.cy.300.fifu

cache/cache-cy.json:
	python translate_cache.py


.PHONY: model
model: build-dev
	docker-compose run -e RUST_BACKTRACE=1 --entrypoint poetry ff_fasttext_api run ffp-convert -f textdims ${INPUT_VEC} -t finalfusion ${OUTPUT_FIFU}


.PHONY: deps
deps: ## Installs dependencies
	@if [ -z "$(EXISTS_FLASK)" ]; then \
	if [ -z "$(EXISTS_POETRY)" ]; then \
		pip -qq install poetry; \
		poetry config virtualenvs.in-project true; \
	fi; \
		poetry install --quiet || poetry install; \
	fi; \

.PHONY: test-component
test-component: deps ## Makes sure dep are installed and runs component tests
	poetry run pytest tests/api

.PHONY: unit
unit: deps ## Makes sure dep are installed and runs unit tests
	poetry run pytest tests/unit

.PHONY: test ## Makes sure dep are installed and runs all tests
test: unit test-component

.PHONY: fmt
fmt: deps ## Makes sure dep are installed and formats code
	poetry run isort ff_fasttext_api
	poetry run black ff_fasttext_api

.PHONY: lint
lint: deps ## Makes sure dep are installed and lints code
	ruff check .

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

