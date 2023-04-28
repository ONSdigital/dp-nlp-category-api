#!/bin/bash -eux

cwd=$(pwd)

export GOPATH=$cwd/go

pushd dp-nlp-category-api
  make build-bin
  mkdir $cwd/build
  cp dist/ff_fasttext_api-0.0.1-py3-none-any.whl ff_fasttext_api-0.0.1.tar.gz $cwd/build
popd
