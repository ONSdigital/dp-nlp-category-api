# https://github.com/python-poetry/poetry/discussions/1879
# to improve ^^

## STAGE 1 - Core package(s)

FROM flaxandteal/ff_fasttext_build:latest as ff

RUN maturin build

## STAGE 2 - API

FROM python:3.11

# Use the build argument within the Dockerfile

RUN mkdir -p /app/category_api
RUN mkdir -p /app/test_data

ENV port=$CATEGORY_API_PORT
ENV host=$CATEGORY_API_HOST

RUN pip install poetry

COPY --from=ff /app/build/target/wheels/*cp39*.whl /app

WORKDIR /app

COPY .env.local /app/
COPY pyproject.toml /app
COPY poetry.lock /app
COPY gunicorn_config.py /app

COPY category_api /app/category_api
COPY test_data /app/test_data

RUN poetry install

# We want to use poetry for consistency and because it is designed to reproducibly
# manage Python - however the link at the top gives ways of doing this multistage,
# which would be slightly nicer.

EXPOSE 28800

ENTRYPOINT poetry run uvicorn category_api.main:app
