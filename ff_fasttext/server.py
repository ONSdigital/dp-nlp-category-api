import logging
from fastapi import FastAPI
from .extract import load

THRESHOLD = 0.4

def make_app(category_manager):
    app = FastAPI()

    @app.get('/categories')
    def get_categories(query: str):
        categories = category_manager.test(query.strip(), 'onyxcats')
        return [
            [float(c[0]), list(c[1])] for c in categories if c[0] > THRESHOLD
        ]

    return app

category_manager = load('test_data/wiki.en.fifu')
app = make_app(category_manager)
