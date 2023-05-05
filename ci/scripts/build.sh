#!/bin/sh

pushd dp-nlp-category-api
  docker login -u $1 -p $2
  make build
  make push-image
popd
