from dynaconf import LazySettings

settings = LazySettings(
    DEBUG_LEVEL_FOR_DYNACONF="DEBUG",
    ENVVAR_PREFIX_FOR_DYNACONF="FF_FASTTEXT_CORE",
    DOTENV_PATH_FOR_DYNACONF=".env",
)
settings.reload()
