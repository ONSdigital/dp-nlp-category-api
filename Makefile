SHELL=sh
MAIN=build-dev

BUILD=build

.PHONY: all
all: build-dev

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
