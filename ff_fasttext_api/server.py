import os
import time
os.environ['DEBUG_LEVEL_FOR_DYNACONF'] = 'DEBUG'

from fastapi import FastAPI
from typing import Optional
from .settings import settings
from datetime import datetime
from ff_fasttext_api.healthcheck import Healthcheck
from bonn.extract import load
from bonn.utils import filter_by_snr
from fastapi import FastAPI

from .logger import configure_logging, setup_logger
from .settings import settings

print("is this start?")
configure_logging()
logger = setup_logger(severity=3)

def make_app(category_manager, health_check):
    app = FastAPI()

    DUMMY_RUN = settings.get("DUMMY_RUN", os.getenv("FF_FASTTEXT_DUMMY_RUN", "") == "1")
    THRESHOLD = settings.get("THRESHOLD", 0.4)

    @app.get("/categories/{cat}")
    def get_category(cat: str, query: str):
        try:
            category = tuple(cat.split("|"))
            scoring = category_manager.test_category(
                query.strip(), category, "onyxcats"
            )
            logger.info(
                event="category tested",
                category=category,
                query=query,
                weightings=scoring["weightings"],
                scoring=scoring["tags"],
            )
        except Exception as e:
            logger.error(
                event="category testing failed",
                exception=str(e),
                query=query,
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
        if DUMMY_RUN:
            logger.warning(
                event="dummy run is enabled, returning empty list", severity=2
            )
            return []

        try:
            categories = category_manager.test(query.strip(), "onyxcats")
            logger.info(
                event="testing categories",
                query=query,
                snr=snr,
            )

            if snr is not None:
                categories = filter_by_snr(categories, snr)
                logger.debug("successfully filtered categories by SNR", snr=snr)
        except Exception as e:
            logger.error(
                event="testing and filtration of categories failed",
                error=str(e),
                severity=1,
            )
            return {
                "message": "Internal Server Error",
                "error code": "",  # to be aggreed upon
            }

        return [
            {"s": float(c[0]), "c": list(c[1])} for c in categories if c[0] > THRESHOLD
        ]

    @app.get("/health")
    def health():
        return health_check.to_json()

    return app

def create_app():
    start_time = datetime.utcnow().isoformat() # The time the app started in UTC

    category_manager = load('test_data/wiki.en.fifu')

    health = Healthcheck(status="OK", version='0.1.0', start_time=start_time, checks=[])

    logger.info("successfully loaded category manager")

    app = make_app(category_manager, health)

    return app
