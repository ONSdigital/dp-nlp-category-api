# FinalFusion FastText embedding

## Download embeddings
Note: I don't recommend the full common crawl or wiki model if you want to try an opq model...
Download one of the fasttext embeddings, eg https://dl.fbaipublicfiles.com/fasttext/supervised-models/dbpedia.bin

## Docker build

To build and run the API using docker:

```
make run
```

To build wheels for distribution, use:

```
make wheels
```

## Manual building

### Install finalfusion utils

``` bash
cd core
RUSTFLAGS="-C link-args=-lcblas -llapack" cargo install finalfusion-utils --features=opq
```

### Optional: Convert the model to quantized fifu format

Note: if you try to use the full wiki bin you'll need about 128GB of RAM...

``` bash
finalfusion quantize -f fasttext -q opq <fasttext.bin> fasttext.fifu.opq
```

### Install deps and build

``` bash
poetry shell
cd core
poetry install
cd ../api
poetry install
exit
```

### Run

```bash
poetry run python -c "from ff_fasttext import FfModel; FfModel('test_data/wiki.en.fifu').eval('Hello')"
```


