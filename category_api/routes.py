import traceback
from typing import Optional

from bonn.utils import filter_by_snr
from fastapi import FastAPI

from category_api.logger import format_errors

from .logger import setup_logging

logger = setup_logging()

try:
    if not app:
        app = FastAPI()
except NameError:
    app = FastAPI()


@app.get("/categories/{cat}")
def get_category(cat: str, query: str):
    try:
        category = tuple(cat.split("|"))
        scoring = app.controllers.category_manager.test_category(
            query.strip(), category, "onyxcats"
        )
        logger.info(
            event="category tested",
            data={
                "category": category,
                "query": query,
                "weightings": scoring["weightings"],
                "scoring": scoring["tags"],
            },
        )
    except Exception as e:
        logger.error(
            event="error retrieving key from database",
            errors=format_errors(e, trace=traceback.format_exc()),
        )

        return {
            "message": "Internal Server Error",
            "error code": 500,
        }

    return {
        "weightings": {w: x for w, x in scoring["weightings"].items()},
        "scoring": {
            w: {
                "overall": float(s["overall"]),
                "vector": float(scoring["vector"]),
                "significance": float(scoring["significance"]),
                "by-classifier": sorted(
                    ([ws, float(wv)] for ws, wv in s["by-classifier"].items()),
                    key=lambda v: v[1],
                    reverse=True,
                ),
            }
            for w, s in scoring["tags"].items()
        },
    }


@app.get("/categories")
def get_categories(query: str, snr: Optional[float] = 1.275):
    if app.settings.DUMMY_RUN:
        logger.warning(event="dummy run is enabled, returning empty list")
        return []

    try:
        categories = app.controllers.category_manager.test(query.strip(), "onyxcats")

        if snr is not None:
            categories = filter_by_snr(categories, snr)
            logger.info(
                event="successfully filtered categories by SNR", data={"snr": snr}
            )

    except Exception as e:
        logger.error(
            event="error retrieving key from database",
            errors=format_errors(e, trace=traceback.format_exc()),
        )

        return {
            "message": "Internal Server Error",
            "error code": 500,
        }

    return [
        {"s": float(c[0]), "c": list(c[1])}
        for c in categories
        if c[0] > app.settings.THRESHOLD
    ]


@app.get("/health")
def health():
    return app.controllers.healthcheck.to_json()
