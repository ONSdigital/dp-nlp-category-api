import json
from datetime import datetime

# Define the check statuses
OK = 'OK'
WARNING = 'WARNING'
ERROR = 'ERROR'

class Healthcheck:
    def __init__(self, status, version, uptime, start_time, checks):
        self.status = status
        self.version = version
        self.uptime = uptime
        self.start_time = start_time
        self.checks = checks

    def to_json(self):
        # Get the current time in UTC
        now = datetime.utcnow().isoformat()

        # Calculate the uptime in seconds
        uptime_sec = self.uptime / 1000

        # Define the healthcheck response
        response = {
            'status': self.status,
            'version': self.version,
            'uptime': uptime_sec,
            'start_time': self.start_time,
            'checks': self.checks,
            'timestamp': now
        }

        # Convert the response to JSON and return it
        return json.dumps(response)