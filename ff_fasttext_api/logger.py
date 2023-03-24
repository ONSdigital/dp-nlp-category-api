import structlog
from datetime import datetime

def configure_logging():
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.JSONRenderer(),
        ],
        context_class=structlog.threadlocal.wrap_dict(dict),
        logger_factory=structlog.stdlib.LoggerFactory(),
    )

def setup_logger(severity):
    return structlog.get_logger(
        namespace="ff_fasttext_api",
        created_at=datetime.utcnow().isoformat(),
        severity=severity,
    )
