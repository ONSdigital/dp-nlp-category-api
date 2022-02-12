from fastapi import FastApi
from .extract import load

THRESHOLD = 0.4

def make_app(category_manager):
    app = FastApi()

    @app.get('/categories')
    def get_categories(query: str):
        categories = category_manager.test(query.strip(), 'onyxcats')
        return [
            c for c in categories if c[1] > THRESHOLD
        ]

    return app

category_manager = load('test_data/wiki.en.fifu')
app = make_app(category_manager)
