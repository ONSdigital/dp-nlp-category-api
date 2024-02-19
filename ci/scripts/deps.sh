#!/bin/bash

if command -v poetry &> /dev/null; then
    echo "Poetry is already installed. Running poetry install."
    poetry install
else
    echo "Poetry not found. Installing Poetry and then running poetry install."
    pip install poetry
    poetry config virtualenvs.in-project true
    poetry install
fi
