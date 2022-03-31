dp-nlp-category-api
================
NLP Category-Matching API

A Rust microservice to match queries on the ONS Website to groupings in the ONS taxonomy

### Getting started

#### Set up taxonomy.json

This should be obtained from ONS and placed in the root directory.

#### Download or create embeddings

These are most simply sourced as [pretrained fifu models](https://finalfusion.github.io/pretrained), but can be dynamically generated
using the embedded FinalFusion libraries.

To build and run the API using docker:

```
make run
```

or, for Welsh,

```
make run-cy
```

To build wheels for distribution, use:

```
make wheels
```

### Manual building

#### Install finalfusion utils

``` bash
cd core
RUSTFLAGS="-C link-args=-lcblas -llapack" cargo install finalfusion-utils --features=opq
```

#### Optional: Convert the model to quantized fifu format

Note: if you try to use the full wiki bin you'll need about 128GB of RAM...

``` bash
finalfusion quantize -f fasttext -q opq <fasttext.bin> fasttext.fifu.opq
```

#### Install deps and build

``` bash
poetry shell
cd core
poetry install
cd ../api
poetry install
exit
```

#### Run

```bash
poetry run python -c "from ff_fasttext import FfModel; FfModel('test_data/wiki.en.fifu').eval('Hello')"
```

### Algorithm

This
