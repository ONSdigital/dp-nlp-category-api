#!/bin/bash -eux

pushd dp-nlp-category-api
  make build
  docker login -u $1 -p $2
  make push-image
popd
