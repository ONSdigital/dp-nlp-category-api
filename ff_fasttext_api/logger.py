import structlog

def setup_logger():
        return structlog.get_logger(
        namespace="ff_fasttext_api",
        processors=[
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(indent=None),
        ],
        context_class=dict,
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

logger = setup_logger()