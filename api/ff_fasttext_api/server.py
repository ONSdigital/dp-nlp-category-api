import logging
import os
from fastapi import FastAPI
from ff_fasttext.extract import load

THRESHOLD = 0.4
DUMMY_RUN = os.getenv('FF_FASTTEXT_DUMMY_RUN', '') == '1'

def make_app(category_manager):
    app = FastAPI()

    @app.get('/categories')
    def get_categories(query: str):
        if DUMMY_RUN:
            return []

        categories = category_manager.test(query.strip(), 'onyxcats')
        return [
            {'s': float(c[0]), 'c': list(c[1])} for c in categories if c[0] > THRESHOLD
        ]

    return app

category_manager = load('test_data/wiki.en.fifu')
app = make_app(category_manager)
