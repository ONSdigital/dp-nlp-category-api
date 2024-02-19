import time

from bonn.settings import settings as settings_bonn
from dynaconf import Dynaconf

current_time = int(time.time())

settings = Dynaconf(
    envvar_prefix="CATEGORY_API",
    load_dotenv=True,
)

settings.reload()

settings.PORT = settings.get("PORT", 28800)
settings.HOST = settings.get("HOST", "0.0.0.0")
settings.NAMESPACE = settings.get("NAMESPACE", "dp_nlp_berlin_api")
settings.FIFU_FILE = settings.get("FIFU_FILE", "test_data/wiki.en.fifu")
settings.DUMMY_RUN = settings.get("DUMMY_RUN", False)
settings.THRESHOLD = settings.get("THRESHOLD", 0.4)
settings.VERSION = "0.1.0"
settings.START_TIME = settings.get("START_TIME", current_time)
settings.GIT_COMMIT = settings.get("GIT_COMMIT")

settings_bonn.reload()


def get_bonn_settings():
    return settings_bonn
