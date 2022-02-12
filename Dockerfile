FROM rust:bullseye as rust_build

RUN mkdir -p /app/build/ff_fasttext
RUN mkdir -p /app/build/test_data
WORKDIR /app/build/test_data
# RUN curl -L -O "...wiki/wiki.en.fifu"
WORKDIR /app/build

COPY Cargo.lock /app/build
COPY Cargo.toml /app/build

RUN apt-get update && apt-get install -y python3-pip liblapack-dev libatlas-base-dev

RUN RUSTFLAGS="-C link-args=-lcblas -llapack" cargo install finalfusion-utils --features=opq

COPY setup.py /app/build
COPY setup.cfg /app/build
COPY pyproject.toml /app/build
COPY poetry.lock /app/build
COPY requirements-dev.txt /app/build
COPY src /app/build/src
COPY ff_fasttext/__init__.py /app/build/ff_fasttext

WORKDIR /app/build

RUN pip install --no-cache-dir --upgrade -r requirements-dev.txt

RUN python3 setup.py develop

FROM python:3-bullseye

RUN mkdir -p /app/ff_fasttext

COPY --from=rust_build /app/build/ff_fasttext/_ff_fasttext.abi3.so /app/ff_fasttext
COPY --from=rust_build /app/build/test_data /app/test_data

RUN pip install poetry
WORKDIR /app

COPY setup.py /app
COPY setup.cfg /app
COPY pyproject.toml /app
COPY poetry.lock /app
COPY requirements-dev.txt /app
COPY ff_fasttext /app/ff_fasttext
# COPY taxonomy.json /app

WORKDIR /app

RUN poetry install

CMD ["poetry", "run", "uvicorn", "ff_fasttext.server:app", "--host", "0.0.0.0", "--port", "80"]
