#!/bin/bash -eux

pushd dp-nlp-category-api
  make build
  cp build/dp-nlp-category-api Dockerfile.concourse ../build
popd
