# https://til.codeinthehole.com/posts/how-to-get-gunicorn-to-log-as-json/

import datetime
import logging
import sys
from category_api.settings import settings

import json_log_formatter

class JsonRequestFormatter(json_log_formatter.JSONFormatter):
    def json_record(
        self,
        event: str,
        extra: dict[str, str | int | float],
        record: logging.LogRecord,
    ) -> dict[str, str | int | float]:
        # Convert the log record to a JSON object.
        # See https://docs.gunicorn.org/en/stable/settings.html#access-log-format

        severity = (
            3 if record.levelname == "INFO" else 1 if record.levelname == "ERROR" else 0
        )
        url = record.args[2]
        if "?" in url:
            path, query = url.split("?", 1)
        else:
            path = url
            query = ""

        return dict(
            namespace=settings.NAMESPACE,
            created_at=datetime.datetime.utcnow().isoformat(timespec="milliseconds") + "Z",
            event="making request",
            data={
                "remote_ip": record.args[0],
            },
            method=record.args[1],
            path=path,
            query=query,
            status=int(record.args[4]),
            severity=severity,
        )


class JsonErrorFormatter(json_log_formatter.JSONFormatter):
    def json_record(
        self,
        event: str,
        extra: dict[str, str | int | float],
        record: logging.LogRecord,
    ) -> dict[str, str | int | float]:
        payload: dict[str, str | int | float] = super().json_record(
            event, extra, record
        )
        payload["namespace"] = settings.NAMESPACE
        # json_log_formatter sets "time" using datetime.utcnow()
        # https://github.com/marselester/json-log-formatter/blob/
        #       bf41c57913a92a9b556d9fc0e3165e97daa38f8e/json_log_formatter/__init__.py#L123)
        payload["created_at"] = payload["time"].isoformat(timespec="milliseconds") + "Z"
        payload["event"] = record.getMessage()
        payload["errors"] = [
            {
                "message": record.getMessage(),
                "data": {
                    "level": record.levelname
                }
            }
        ]
        payload["severity"] = 3 if record.levelname == "INFO" else 1 if record.levelname == "ERROR" else 0
        payload.pop('taskName', None)
        payload.pop('color_message', None)
        payload.pop('time', None)
        payload.pop('message', None)

        return payload


# Ensure the two named loggers that Gunicorn uses are configured to use a custom
# JSON formatter.
logconfig_dict = {
    "version": 1,
    "formatters": {
        "json_request": {
            "()": JsonRequestFormatter,
        },
        "json_error": {
            "()": JsonErrorFormatter,
        },
    },
    "handlers": {
        "json_request": {
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
            "formatter": "json_request",
        },
        "json_error": {
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
            "formatter": "json_error",
        },
    },
    "root": {"level": "INFO", "handlers": []},
    "loggers": {
        "uvicorn.access": {
            "level": "INFO",
            "handlers": ["json_request"],
            "propagate": False,
        },
        "uvicorn.error": {
            "level": "INFO",
            "handlers": ["json_error"],
            "propagate": False,
        },
    },
}

bind = f"0.0.0.0:{settings.PORT}"
timeout = int(settings.TIMEOUT or 0)
