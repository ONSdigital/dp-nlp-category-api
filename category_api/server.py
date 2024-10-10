import importlib.util
from contextlib import asynccontextmanager

import bonn
from bonn.extract import CategoryManager
from fastapi import FastAPI

from category_api.data import retrieve
from category_api.healthcheck import Healthcheck
from category_api.logger import setup_logging
from category_api.settings import get_bonn_settings, settings

logger = setup_logging()

class Controllers:
    category_manager: CategoryManager
    healthcheck: Healthcheck


def make_app(controllers, settings, settings_bonn):
    app = FastAPI(lifespan=lifespan)
    app.controllers = controllers
    app.settings = settings
    app.settings_bonn = settings_bonn

    routes_spec = importlib.util.find_spec("category_api.routes")
    routes = importlib.util.module_from_spec(routes_spec)
    routes.app = app
    routes_spec.loader.exec_module(routes)

    return app


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(
        event="startup configuration",
        data={
            "app_settings": {
                "DEBUG_LEVEL_FOR_DYNACONF": app.settings.DEBUG_LEVEL_FOR_DYNACONF,
                "DUMMY_RUN": app.settings.DUMMY_RUN,
                "FIFU_FILE": app.settings.FIFU_FILE,
                "GIT_COMMIT": app.settings.GIT_COMMIT,
                "HOST": app.settings.HOST,
                "PORT": app.settings.PORT,
                "START_TIME": app.settings.START_TIME,
                "TIMEOUT": app.settings.TIMEOUT,
                "THRESHOLD": app.settings.THRESHOLD,
                "VERSION": app.settings.VERSION,
            },
            "bonn_settings": {
                "CACHE_TARGET": app.settings_bonn.CACHE_TARGET,
                "REBUILD_CACHE": app.settings_bonn.REBUILD_CACHE,
                "TAXONOMY_LOCATION": app.settings_bonn.TAXONOMY_LOCATION,
                "WEIGHTING__C": app.settings_bonn.WEIGHTING.C,
                "WEIGHTING__SC": app.settings_bonn.WEIGHTING.SC,
                "WEIGHTING__SSC": app.settings_bonn.WEIGHTING.SSC,
                "WEIGHTING__WC": app.settings_bonn.WEIGHTING.WC,
                "WEIGHTING__WSSC": app.settings_bonn.WEIGHTING.WSSC,
            },
        },
    )

    app.controllers.healthcheck = Healthcheck(status="OK", checks=[])
    with retrieve(app.settings, app.settings_bonn) as (settings, settings_bonn):
        app.settings = settings
        app.settings_bonn = settings_bonn
        app.controllers.category_manager = bonn.extract.load(
            app.settings.FIFU_FILE, app.settings_bonn
        )
        yield


def create_app():
    controllers = Controllers()
    settings_bonn = get_bonn_settings()
    app = make_app(controllers, settings, settings_bonn)

    return app
