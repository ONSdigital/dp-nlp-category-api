from dynaconf import LazySettings
settings = LazySettings(
    load_dotenv=True,
    DEBUG_LEVEL_FOR_DYNACONF="DEBUG",
    ENVVAR_PREFIX_FOR_DYNACONF='FF_FASTTEXT_API'
)
settings.reload()
