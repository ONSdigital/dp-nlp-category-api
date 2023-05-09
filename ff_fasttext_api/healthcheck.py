from datetime import datetime
import subprocess
import time
import sys

# Define the check statuses
OK = 'OK'
WARNING = 'WARNING'
ERROR = 'ERROR'

class Healthcheck:
    # TO-DO: update healthcheck with image build time
    def __init__(self, status, version, build_time, checks):
        self.status = status
        self.version = {
            "version": version,
            "build_time": build_time,
            "git_commit": self.get_last_commit(),
            "language": "python",
            "language_version": sys.version,
        }
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
        last_commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'])
        return last_commit.decode('utf-8').strip()
    
    def set_start_time(self, start_time):
        start_time = datetime.datetime.now()
        formatted_time = start_time.strftime('%Y-%m-%dT%H:%M:%S%z')
        
        self.start_time = formatted_time
    
    def get_uptime(self):
        uptime = time.time()
        start_time = datetime.fromisoformat(self.start_time)
        start_time_unix = int(start_time.timestamp())

        uptime = round((uptime - start_time_unix)*1000)

        return uptime