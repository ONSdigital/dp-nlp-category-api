from dynaconf import Dynaconf

settings = Dynaconf(
    DEBUG_LEVEL_FOR_DYNACONF="DEBUG",
    ENVVAR_PREFIX_FOR_DYNACONF="FF_FASTTEXT_API",
    envvar_prefix="FF_FASTTEXT_API",
    load_dotenv=True, 
)

settings.reload()
PORT = settings.get("CATEGORY_API_PORT", 28800)
HOST = settings.get("CATEGORY_API_HOST", "0.0.0.0")

FIFU_FILE = settings.get("FIFU_FILE", "test_data/wiki.en.fifu")


DUMMY_RUN = settings.get("DUMMY_RUN", False)
THRESHOLD = settings.get("THRESHOLD", 0.4)


# VERSION = settings.get("VERSION", "0.1.0")
VERSION = "0.1.0"
START_TIME = settings.get("START_TIME")
GIT_COMMIT = settings.get("GIT_COMMIT")