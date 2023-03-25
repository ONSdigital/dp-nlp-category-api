#!/bin/bash -eux

pushd dp-nlp-search-scrubber
  make build
  cp build/dp-nlp-search-scrubber Dockerfile.concourse ../build
popd
