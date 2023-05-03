from datetime import datetime
import subprocess
import time
import sys

# Define the check statuses
OK = 'OK'
WARNING = 'WARNING'
ERROR = 'ERROR'

class Healthcheck:
    def __init__(self, status, version, start_time, checks):
        self.status = status
        self.version = {
            "version": version,
            "git_commit": self.get_last_commit(),
            "language": "python",
            "language_version": sys.version,
        }
        self.start_time = start_time
        self.checks = checks

    def to_json(self):
        response = {
            'status': self.status,
            'version': self.version,
            'uptime': self.get_uptime(),
            'start_time': self.start_time,
            'checks': self.checks
        }

        return response
    
    def get_last_commit(self):
        last_commit = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('utf-8').strip()
        return last_commit
    
    def get_uptime(self):
        uptime = time.time()
        start_time = datetime.fromisoformat(self.start_time)
        start_time_unix = int(start_time.timestamp())

        uptime = round((uptime - start_time_unix)*1000)

        return uptime