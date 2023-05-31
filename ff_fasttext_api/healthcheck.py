from ff_fasttext_api.config import start_time, commit, version
import sys
import time
from datetime import datetime

# Define the check statuses
OK = "OK"
WARNING = "WARNING"
ERROR = "ERROR"


class Healthcheck:
    def __init__(self, status, checks):
        formatted_start_time = datetime.fromtimestamp(int(start_time))

        build_time = datetime.now()

        self.start_time = formatted_start_time.strftime('%Y-%m-%dT%H:%M:%S%z')

        self.status = status
        self.version = {
            "version": version,
            "build_time": build_time,
            "git_commit": commit,
            "language": "python",
            "language_version": sys.version,
        }
        self.checks = checks

    def to_json(self):
        response = {
            "status": self.status,
            "version": self.version,
            "uptime": self.get_uptime(),
            "start_time": self.start_time,
            "checks": self.checks,
        }

        return response

    def get_uptime(self):
        uptime = time.time()
        start_time = datetime.fromisoformat(self.start_time)
        start_time_unix = int(start_time.timestamp())

        uptime = round((uptime - start_time_unix) * 1000)

        return uptime
