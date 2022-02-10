# FinalFusion FastText embedding

## Download embeddings
Note: I don't recommend the full common crawl or wiki model if you want to try an opq model...
Download one of the fasttext embeddings, eg https://dl.fbaipublicfiles.com/fasttext/supervised-models/dbpedia.bin

## Install finalfusion utils

``` bash
RUSTFLAGS="-C link-args=-lcblas -llapack" cargo install finalfusion-utils --features=opq
```

## Optional: Convert the model to quantized fifu format

Note: if you try to use the full wiki bin you'll need about 128GB of RAM...

``` bash
finalfusion quantize -f fasttext -q opq <fasttext.bin> fasttext.fifu.opq
```

## Install deps

``` bash
pip install -r requirements-dev.txt
```

## Build

``` bash
python setup.py develop
```

## Run

```bash
python -c "from ff_fasttext import FfModel; FfModel('test_data/wiki.en.fifu').eval('Hello')"
```


