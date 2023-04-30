from datetime import datetime
import subprocess
import time
import sys
import os

# Define the check statuses
OK = 'OK'
WARNING = 'WARNING'
ERROR = 'ERROR'
commit_sha = os.environ['COMMIT_SHA']

class Healthcheck:
    def __init__(self, status, version, uptime, start_time, checks):
        self.status = status
        self.version = {
            "version": version,
            "git_commit": commit_sha,
            "language": "python",
            "language_version": sys.version,
        }
        self.uptime = uptime
        self.start_time = start_time
        self.checks = checks

    def to_json(self):
        now = datetime.utcnow()

        response = {
            'status': self.status,
            'version': self.version,
            'uptime': self.get_uptime(self.uptime),
            'start_time': self.start_time,
            'timestamp': now,
            'checks': self.checks
        }

        return response
    
    # def get_last_commit(self):
    #     last_commit = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('utf-8').strip()
    #     return last_commit
    
    def get_uptime(self, start_time):
        uptime = time.time()
        intervals = (
            ('w', 604800),
            ('d', 86400),
            ('h', 3600),
            ('m', 60),
            ('s', 1),
        )
        uptime = round(uptime - start_time)

        parts = []
        for name, count in intervals:
            value = int(uptime // count)
            if value:
                uptime -= value * count
                parts.append(f"{value} {name}")

        return ', '.join(parts)
    