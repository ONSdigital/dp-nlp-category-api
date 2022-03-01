# https://github.com/python-poetry/poetry/discussions/1879
# to improve ^^

## STAGE 1 - Core package(s)

# https://github.com/python-poetry/poetry/discussions/1879
# to improve ^^

## STAGE 1 - Core package(s)

FROM konstin2/maturin as maturin

RUN mkdir -p /app/build/ff_fasttext
WORKDIR /app/build/test_data
# RUN curl -L -O "...wiki/wiki.en.fifu"
WORKDIR /app/build

RUN yum install -y lapack-devel atlas-devel

COPY core/Cargo.lock /app/build
COPY core/Cargo.toml /app/build
COPY core/LICENSE.md /app/build

RUN RUSTFLAGS="-L /usr/lib64/atlas -C link-args=-lcblas -llapack" cargo install finalfusion-utils --features=opq

COPY core/pyproject.toml /app/build
COPY core/src /app/build/src
COPY core/ff_fasttext /app/build/ff_fasttext

WORKDIR /app/build

RUN maturin build

## STAGE 2 - API

FROM python:3.9

RUN mkdir -p /app/ff_fasttext

RUN pip install poetry

COPY --from=maturin /app/build/target/wheels/*cp39*.whl /app

WORKDIR /app

COPY api/pyproject.toml /app
RUN sed -i "s/ff_fasttext # Replace with wheel.*/ff_fasttext = { \"file\" = \"$(ls -1 *.whl)\" }/" pyproject.toml

COPY api/poetry.lock /app
COPY api/ff_fasttext_api /app/ff_fasttext_api

RUN poetry install

# We want to use poetry for consistency and because it is designed to reproducibly
# manage Python - however the link at the top gives ways of doing this multistage,
# which would be slightly nicer.
CMD ["poetry", "run", "uvicorn", "ff_fasttext_api.server:app", "--host", "0.0.0.0", "--port", "80"]


## STAGE 2 - API

FROM python:3.9

RUN mkdir -p /app/ff_fasttext

RUN pip install poetry

COPY --from=maturin /app/build/target/wheels/*cp39*.whl /app

WORKDIR /app

COPY api/pyproject.toml /app
RUN sed -i "s/ff_fasttext # Replace with wheel.*/ff_fasttext = { \"file\" = \"$(ls -1 *.whl)\" }/" pyproject.toml

COPY api/poetry.lock /app
COPY api/ff_fasttext_api /app/ff_fasttext_api

RUN poetry install

# We want to use poetry for consistency and because it is designed to reproducibly
# manage Python - however the link at the top gives ways of doing this multistage,
# which would be slightly nicer.
CMD ["poetry", "run", "uvicorn", "ff_fasttext_api.server:app", "--host", "0.0.0.0", "--port", "3003"]