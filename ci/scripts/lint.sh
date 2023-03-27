#!/bin/bash -eux

pushd dp-nlp-category-api
  env
  mkdir -p .poetry
  ls .poetry
  make lint
  ls .poetry
  ls .venv
popd
