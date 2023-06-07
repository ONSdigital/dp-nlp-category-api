# https://github.com/python-poetry/poetry/discussions/1879
# to improve ^^

## STAGE 1 - Core package(s)

FROM flaxandteal/ff_fasttext_build:latest as ff

RUN maturin build

## STAGE 2 - API

FROM python:3.9

# Declare the host and port
ARG HOST
ARG PORT

# Use the build argument within the Dockerfile
ENV host=$HOST
ENV port=$PORT

RUN mkdir -p /app/ff_fasttext
RUN mkdir -p /app/test_data

RUN pip install poetry

COPY --from=ff /app/build/target/wheels/*cp39*.whl /app

WORKDIR /app

COPY .env /app/
COPY pyproject.toml /app
COPY poetry.lock /app

COPY api.py /app/
COPY settings.py /app/

COPY ff_fasttext_api /app/ff_fasttext_api
COPY test_data /app/test_data

RUN poetry install

# We want to use poetry for consistency and because it is designed to reproducibly
# manage Python - however the link at the top gives ways of doing this multistage,
# which would be slightly nicer.
EXPOSE $port

ENTRYPOINT poetry run uvicorn api:app --host $host --port $port
