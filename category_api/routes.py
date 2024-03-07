import traceback
from typing import Optional

from bonn.utils import filter_by_snr
from fastapi import FastAPI

from category_api.logger import setup_logging

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
    except Exception as exc:
        logger.error(
            event="category testing failed",
            data={
                "query": query,
                "category": cat,
            },
            error=traceback.format_exception(exc),
        )
        return {
            "message": "Internal Server Error",
            "error code": "",  # to be agreed upon
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
        logger.info(
            event="testing categories",
            data={
                "query": query,
                "snr": snr,
            },
        )

        if snr is not None:
            categories = filter_by_snr(categories, snr)
            logger.info(event="successfully filtered categories by SNR", data={snr})

    except Exception as exc:
        traceback.format_exception(exc)
        logger.error(
            event="testing and filtration of categories failed",
            data={
                "query": query,
                "snr": snr,
            },
            error=traceback.format_exception(exc),
        )
        return {
            "message": "Internal Server Error",
            "error code": "",  # to be aggreed upon
        }

    return [
        {"s": float(c[0]), "c": list(c[1])}
        for c in categories
        if c[0] > app.settings.THRESHOLD
    ]


@app.get("/health")
def health():
    return app.controllers.healthcheck.to_json()
