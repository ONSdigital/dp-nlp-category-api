import logging
from typing import Optional
import os
os.environ['DEBUG_LEVEL_FOR_DYNACONF'] = 'DEBUG'
from fastapi import FastAPI
from .settings import settings

from ff_fasttext.extract import load
from ff_fasttext.utils import filter_by_snr

def make_app(category_manager):
    app = FastAPI()

    DUMMY_RUN = settings.get('DUMMY_RUN', os.getenv('FF_FASTTEXT_DUMMY_RUN', '') == '1')
    THRESHOLD = settings.get('THRESHOLD', 0.4)

    @app.get('/categories/{cat}')
    def get_category(cat: str, query: str):
        category = tuple(cat.split('|'))
        scoring = category_manager.test_category(query.strip(), category, 'onyxcats')
        return {
            'weightings': {w: x for w, x in scoring['weightings'].items()},
            'scoring': {
                w: {
                    'overall': float(s['overall']),
                    'vector': float(scoring['vector']),
                    'significance': float(scoring['significance']),
                    'by-classifier': sorted(
                        (
                            [ws, float(wv)]
                            for ws, wv in s['by-classifier'].items()
                        ),
                        key=lambda v: v[1],
                        reverse=True
                    )
                } for w, s in scoring['tags'].items()
            }
        }

    @app.get('/categories')
    def get_categories(query: str, snr: Optional[float] = 1.275):
        if DUMMY_RUN:
            return []

        categories = category_manager.test(query.strip(), 'onyxcats')
        if snr is not None:
            categories = filter_by_snr(categories, snr)
        return [
            {'s': float(c[0]), 'c': list(c[1])} for c in categories if c[0] > THRESHOLD
        ]

    @app.get('/health')
    def health():
        return 'OK'

    return app

def create_app():
    category_manager = load('test_data/wiki.en.fifu')
    app = make_app(category_manager)
    return app
