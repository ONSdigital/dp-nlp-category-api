import tempfile
from contextlib import ExitStack, contextmanager
from urllib.parse import urlparse

import boto3

from .logger import setup_logging

logger = setup_logging()

RETRIEVABLE_FILE_KEYS = [
    # is bonn setting, key
    (True, "CACHE_TARGET"),
    (False, "FIFU_FILE"),
    (True, "TAXONOMY_LOCATION"),
]


@contextmanager
def _make_temporary_files(settings, settings_bonn):
    url = urlparse(settings.CACHE_S3_BUCKET)
    logger.info(event=f"S3 bucket for cache setup up to: {url}")

    s3 = boto3.client("s3")
    temporary_files = []
    with ExitStack() as stack:
        for is_bonn, key in RETRIEVABLE_FILE_KEYS:
            filename = (settings_bonn if is_bonn else settings)[key]
            try:
                # Check this is not a resolvable local path
                open(filename, "r")
            except OSError:
                temporary_file = stack.enter_context(tempfile.NamedTemporaryFile())
                with open(temporary_file.name, "wb") as fh:
                    s3.download_fileobj(url.hostname, filename, fh)

                logger.info(event=f"retrieved cached file ({key}: {filename})")
                temporary_files.append((is_bonn, key, temporary_file))
            else:
                logger.info(
                    event=f"used local path rather than cached file ({key}: {filename})"
                )
        yield temporary_files


@contextmanager
def retrieve(settings, settings_bonn):
    if "CACHE_S3_BUCKET" in settings and settings.CACHE_S3_BUCKET:
        with _make_temporary_files(settings, settings_bonn) as ntf:
            for is_bonn, key, temporary_file in ntf:
                (settings_bonn if is_bonn else settings)[key] = temporary_file.name
            yield settings, settings_bonn
    else:
        yield settings, settings_bonn
